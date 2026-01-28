import qrcode
import os

# Data to encode - This is the "Key" to unlock the section
# Currently the app accepts ANY code, but this is the "official" one.
data = "Unlock_AV_Salon_Hub"

# Create QR Code object
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add data
qr.add_data(data)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image(fill_color="#4CAF50", back_color="white") # Green color for "Unlock"

# Save it to the web assets folder
output_path = os.path.join("web", "assets", "unlock_hub_qr.png")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path)

print(f"QR code generated at {output_path}")
