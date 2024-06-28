import tkinter as tk
from tkinter import filedialog
import requests
from PIL import Image, ImageTk
from client import login

import socket

# URL of your Flask server
SERVER_URL = 'http://84.90.102.75:59000'

CENTRAL_IP = '192.168.0.31'
CENTRAL_PORT = 50000

user_id = login("filipe", "pass")

def send_img(user_id, img_path, type):
    files = {'img': open(img_path, 'rb')}
    url = f'{SERVER_URL}/image'
    headers = {'Authorization': user_id, 'typ': type}

    response = requests.post(url, files=files, headers=headers)
    if response.status_code == 201:
        print("Data sent successfully")
        result_label.config(text="Data sent successfully")
    else:
        print("Failed to send data. Status code:", response.status_code)
        result_label.config(text=f"Failed to send data. Status code: {response.status_code}")

def send_image(image_type):
    file_path = filedialog.askopenfilename()
    if file_path:
        send_img(user_id, file_path, image_type)

def take_picture(argument):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CENTRAL_IP, CENTRAL_PORT))
            s.sendall(argument.encode('utf-8'))
            s.close()
    except Exception as e:
        print(e)

# Initialize the main window
root = tk.Tk()
root.title("SECA - Image manual sender")

# Load the background image
bg_image_path = "background.png"  # Replace with your background image path
bg_image = Image.open(bg_image_path)
bg_width, bg_height = bg_image.size
bg_image = ImageTk.PhotoImage(bg_image)

# Set the window size to the size of the background image
root.geometry(f"{bg_width}x{bg_height}")

# Create a Canvas widget and add the background image
canvas = tk.Canvas(root, width=bg_width, height=bg_height)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_image, anchor="nw")

# Add widgets on top of the canvas
upload_tomato_button = tk.Button(root, text="Send Tomato Image", command=lambda: send_image('tomato'))
upload_disease_button = tk.Button(root, text="Send Disease Image", command=lambda: send_image('disease'))
take_picture_1_button = tk.Button(root, text="Take Picture Tomato", command=lambda: take_picture('tomato'))
take_picture_2_button = tk.Button(root, text="Take Picture Disease", command=lambda: take_picture('disease'))

# Position the buttons on the canvas
canvas.create_window(bg_width/2, bg_height/2 - 35, window=take_picture_1_button)
canvas.create_window(bg_width/2, bg_height/2, window=take_picture_2_button)
canvas.create_window(bg_width/2, bg_height/2 + 35, window=upload_tomato_button)
canvas.create_window(bg_width/2, bg_height/2 + 70, window=upload_disease_button)

result_label = tk.Label(root, text="", fg="white")  # Set only the text color
canvas.create_window(bg_width//2, bg_height/2 + 105, window=result_label)

root.mainloop()
