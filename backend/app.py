from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime

from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='../web', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')

# Use env var for DB if available (Render provides DATABASE_URL), otherwise local sqlite
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1) # SQLAlchemy fix for Render
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///appointments_v3.db'

# Absolute path for uploads
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# web folder is sibling to backend folder
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, '../web/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max

# Ensure upload dir exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/health')
def health_check():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_type = 'PostgreSQL' if 'postgres' in db_uri else 'SQLite'
    is_live = 'postgres' in db_uri
    return jsonify({
        'status': 'online', 
        'database': db_type, 
        'using_live_db': is_live,
        'timestamp': datetime.utcnow().isoformat()
    })

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

CORS(app, supports_credentials=True) # Enable CORS with cookies

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    filename = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    __table_args__ = (db.UniqueConstraint('date', 'time', name='unique_appointment_slot'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending') # New Field
    username = db.Column(db.String(80)) # Link to user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Init ---
def init_db():
    with app.app_context():
        db.create_all()
        
        # Seed Admin
        if not User.query.filter_by(username='bhumesh').first():
            admin_pw = os.environ.get('ADMIN_PASSWORD', 'bhumesh@123')
            hashed_pw = bcrypt.generate_password_hash(admin_pw).decode('utf-8')
            admin = User(username='bhumesh', password=hashed_pw, role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin 'bhumesh' seeded.")

# --- Routes ---

@app.route('/api/current_user', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({'username': current_user.username, 'role': current_user.role})
    return jsonify({'username': None, 'role': None}) # Use 200 OK, just no user

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    
    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user, remember=True)
        return jsonify({'message': 'Login successful', 'role': user.role, 'username': user.username})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

@app.route('/api/book', methods=['POST'])
def book_appointment():
    data = request.json
    
    # If logged in, use current_user.username, else try data['username'] or None
    username = current_user.username if current_user.is_authenticated else data.get('username')

    new_appt = Appointment(
        name=data['name'],
        phone=data['phone'],
        service=data['service'],
        date=data['date'],
        time=data['time'],
        username=username,
        status='pending' # Explicitly set default
    )
    
    try:
        db.session.add(new_appt)
        db.session.commit()
        return jsonify({'message': 'Booked!', 'id': new_appt.id}), 201
    except Exception as e:
        db.session.rollback()
        # Check for integrity error (generic catch for now, but usually it's the unique constraint)
        if 'UNIQUE constraint failed' in str(e) or 'unique_appointment_slot' in str(e):
             return jsonify({'error': 'This time slot is already booked. Please choose another time.'}), 409
        return jsonify({'error': 'An error occurred during booking.'}), 500

@app.route('/api/my-bookings', methods=['GET'])
@login_required
def get_my_bookings():
    # Only get bookings for current user
    appts = Appointment.query.filter_by(username=current_user.username).order_by(Appointment.created_at.desc()).all()
    
    results = []
    for appt in appts:
        results.append({
            'id': appt.id,
            'service': appt.service,
            'date': appt.date,
            'time': appt.time,
            'status': appt.status
        })
    return jsonify(results)

@app.route('/appointments', methods=['GET'])
def get_all_appointments():
    # Ideally should be admin only
    if not current_user.is_authenticated or current_user.role != 'admin':
         return jsonify({'error': 'Unauthorized'}), 403

    appts = Appointment.query.order_by(Appointment.created_at.desc()).all()
    results = [{
        'id': a.id, 'name': a.name, 'phone': a.phone, 
        'service': a.service, 'date': a.date, 'time': a.time, 
        'username': a.username, 'status': a.status
    } for a in appts]
    return jsonify(results)

@app.route('/api/appointments/<int:appt_id>/status', methods=['PUT'])
@login_required
def update_appointment_status(appt_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.json
    new_status = data.get('status')
    
    if new_status not in ['confirmed', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
        
    appt = Appointment.query.get(appt_id)
    if not appt:
        return jsonify({'error': 'Appointment not found'}), 404
        
    appt.status = new_status
    db.session.commit()
    
    return jsonify({'message': f'Appointment {new_status}'})

@app.route('/api/appointments/clear-pending', methods=['POST'])
@login_required
def clear_pending_appointments():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        # Update all pending appointments to rejected
        count = Appointment.query.filter_by(status='pending').update({Appointment.status: 'rejected'})
        db.session.commit()
        return jsonify({'message': f'Rejected {count} pending appointments'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Ideally @login_required + role check
    total_bookings = Appointment.query.count()
    total_users = User.query.count()
    
    confirmed = Appointment.query.filter_by(status='confirmed').count()
    rejected = Appointment.query.filter_by(status='rejected').count()
    pending = Appointment.query.filter_by(status='pending').count()
    
    # Calculate today's confirmed bookings
    # Note: date is stored as String YYYY-MM-DD
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_confirmed = Appointment.query.filter_by(status='confirmed', date=today_str).count()
    
    return jsonify({
        'total_bookings': total_bookings, 
        'total_users': total_users,
        'confirmed': confirmed,
        'rejected': rejected,
        'pending': pending,
        'today_confirmed': today_confirmed
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role} for u in users])

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if user.username == 'bhumesh':
        return jsonify({'error': 'Cannot delete main admin'}), 403
        
    db.session.delete(user)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

# --- Book Library Routes ---
@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return jsonify([{
        'id': b.id,
        'title': b.title,
        'author': b.author,
        'description': b.description,
        'filename': b.filename
    } for b in books])

@app.route('/api/books', methods=['POST'])
@login_required
def upload_book():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        # To prevent overwrites, maybe prepend timestamp
        unique_filename = f"{int(datetime.now().timestamp())}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        
        new_book = Book(
            title=request.form.get('title'),
            author=request.form.get('author'),
            description=request.form.get('description'),
            filename=unique_filename
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book uploaded successfully'}), 201
    
    return jsonify({'error': 'Invalid file type. Only PDF allowed.'}), 400

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # Try delete file
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], book.filename))
    except Exception as e:
        print(f"Error deleting file: {e}") 
        # proceed to delete record anyway
        
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})

# --- Daily Access Code Logic ---
import random

def get_daily_code():
    today_seed = datetime.now().strftime('%Y%m%d')
    random.seed(today_seed)
    # Generate 4 digit code (1000-9999)
    return str(random.randint(1000, 9999))

@app.route('/api/access-code', methods=['GET'])
@login_required
def get_access_code():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'code': get_daily_code()})

@app.route('/api/verify-code', methods=['POST'])
def verify_access_code():
    data = request.json
    submitted_code = data.get('code')
    
    if submitted_code == get_daily_code():
        return jsonify({'message': 'Access granted', 'success': True})
    return jsonify({'error': 'Invalid code', 'success': False}), 401

# Initialize DB (Run on import so Gunicorn creates tables)
with app.app_context():
    db.create_all()
    # Check if admin exists logic is inside init_db, but init_db duplicates create_all
    # Let's just call init_db() directly if we want the seeding
    
init_db()

if __name__ == '__main__':
    print("Secure Server Starting...")
    # debug=False for production simulation
    app.run(debug=True, port=5000) 
