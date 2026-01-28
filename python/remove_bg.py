from PIL import Image

def remove_black_background(input_path, output_path):
    img = Image.open(input_path)
    img = img.convert("RGBA")
    
    datas = img.getdata()
    
    newData = []
    for item in datas:
        # Check if pixel is close to black (adjust threshold as needed)
        if item[0] < 50 and item[1] < 50 and item[2] < 50:
            newData.append((255, 255, 255, 0)) # Make it transparent
        else:
            newData.append(item)
            
    img.putdata(newData)
    img.save(output_path, "PNG")
    print("Successfully saved transparent logo")

if __name__ == "__main__":
    remove_black_background(r"d:\anti\web\assets\logo.png", r"d:\anti\web\assets\logo.png")
