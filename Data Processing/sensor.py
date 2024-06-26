import requests
import json
import random
import time
import datetime

from client import login

# URL of your Flask server
SERVER_URL = 'http://84.90.102.75:59000'

# Function to generate sensor data
def generate_sensor_data(node_id):
    # Get current date and time
    now = datetime.datetime.now()

    # Random air temperature based on season and time of day
    month = now.month
    hour = now.hour

    # Air humidity based on time of day (higher in the morning)
    if 6 <= hour <= 10:
        air_humidity = round(random.uniform(75.0, 85.0), 2)  # Higher humidity in the morning
        luminosity = round(random.uniform(800.0, 1200.0), 2)  # Higher luminosity during the day
    elif 11 <= hour <= 18:
        air_humidity = round(random.uniform(60.0, 75.0), 2)  # Moderate humidity during the day
        luminosity = round(random.uniform(800.0, 1200.0), 2)  # Higher luminosity during the day
    else:
        air_humidity = round(random.uniform(70.0, 80.0), 2)  # Slightly higher humidity in the evening
        luminosity = round(random.uniform(100.0, 300.0), 2)  # Lower luminosity at night

    # Soil humidity based on season and time of day
    if 6 <= hour <= 18:  # Daytime
        if 3 <= month <= 5:  # Spring
            soil_humidity = round(random.uniform(45.0, 55.0), 2)  # Moderate soil humidity in spring
            air_temp = round(random.uniform(15.0, 25.0), 2)  # Warmer temperatures during the day
        elif 6 <= month <= 8:  # Summer
            soil_humidity = round(random.uniform(35.0, 45.0), 2)  # Lower soil humidity in summer
            air_temp = round(random.uniform(20.0, 30.0), 2)  # Higher temperatures during the day
        elif 9 <= month <= 11:  # Autumn
            soil_humidity = round(random.uniform(45.0, 55.0), 2)  # Moderate soil humidity in autumn
            air_temp = round(random.uniform(15.0, 25.0), 2)  # Mild temperatures during the day
        else:  # Winter
            soil_humidity = round(random.uniform(50.0, 60.0), 2)  # Slightly higher soil humidity in winter
            air_temp = round(random.uniform(10.0, 15.0), 2)  # Cooler temperatures during the day
    else:  # Nighttime
        if 3 <= month <= 5:  # Spring
            soil_humidity = round(random.uniform(40.0, 50.0), 2)  # Moderate soil humidity in spring
            air_temp = round(random.uniform(10.0, 15.0), 2)  # Cooler temperatures at night
        elif 6 <= month <= 8:  # Summer
            soil_humidity = round(random.uniform(30.0, 40.0), 2)  # Lower soil humidity in summer nights
            air_temp = round(random.uniform(15.0, 20.0), 2)  # Slightly cooler temperatures at night
        elif 9 <= month <= 11:  # Autumn
            soil_humidity = round(random.uniform(40.0, 50.0), 2)  # Moderate soil humidity in autumn nights
            air_temp = round(random.uniform(10.0, 15.0), 2)  # Cooler temperatures at night
        else:  # Winter
            soil_humidity = round(random.uniform(45.0, 55.0), 2)  # Moderate soil humidity in winter nights
            air_temp = round(random.uniform(5.0, 10.0), 2)  # Colder temperatures at night

    # Random battery voltage between 3.3V and 4.5V
    vbat = round(random.uniform(3.3, 4.5), 2)

    # Create JSON payload
    data = {
        'node_id': node_id,
        'air_temp': air_temp,
        'air_humidity': air_humidity,
        'soil_humidity': soil_humidity,
        'luminosity': luminosity,
        'vbat': vbat
    }

    return data

# Function to send sensor data to server
def send_sensor_data(user_id, data):
    try:
        # Construct URL for the endpoint to send measurements
        url = f'{SERVER_URL}/measurements'
        print("Using:", url)

        # Set Authorization header with user ID
        headers = {'Authorization': user_id}

        # Send POST request to server
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print("Data sent successfully")
        else:
            print("Failed to send data. Status code:", response.status_code)
    except Exception as e:
        print("Exception occurred while sending data:", e)

def send_img(user_id):
    files = {'img': open("tomatos.jpg", 'rb')}
    url = f'{SERVER_URL}/image'
    headers = {'Authorization': user_id}

    response = requests.post(url, files=files, headers=headers)
    if response.status_code == 201:
        print("Data sent successfully")
    else:
        print("Failed to send data. Status code:", response.status_code)

def get_image(user_id, output_name):
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/image'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id, 'opt': "img"}
        # Attempt to get image
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(output_name, 'wb') as f:
                f.write(response.content)
        else:
            print("Failed to get data. Status code:", response.status_code)
            return
        # Attempt to get image data
        headers = {'Authorization': user_id, 'opt': "data"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            print("Failed to get data. Status code:", response.status_code)
            return
    except Exception as e:
        print("Exception occurred while getting data:", e)    

def get_disease(user_id, output_name):
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/image'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id, 'opt': "img", 'typ': "disease"}
        # Attempt to get image
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(output_name, 'wb') as f:
                f.write(response.content)
        else:
            print("Failed to get data. Status code:", response.status_code)
            return
        # Attempt to get image data
        headers = {'Authorization': user_id, 'opt': "data", 'typ': "disease"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            print("Failed to get data. Status code:", response.status_code)
            return
    except Exception as e:
        print("Exception occurred while getting data:", e)



if __name__ == '__main__':
    # List of node IDs
    NODES = ['node1', 'node2', 'node3', 'tomato']

    # Prompt user to input user ID
    user_id = login("filipe", "pass")
    send_img(user_id)

    # Construct URL for the endpoint to retrieve the list of nodes
    # get_disease(user_id, 'teste.png')

    # print(get_image(user_id, "testi.jpg"))
    #headers = {'Authorization': user_id}
    #response = requests.get('http://192.168.0.36:5000/prevision', headers=headers)
    #if response.status_code == 200:
    #    with open("prevision.jpg", 'wb') as f:
    #        f.write(response.content)
    exit
    """
    try:
        while True:
            # Generate sensor data
            for node in NODES:
                sensor_data = generate_sensor_data(node)
                # Send sensor data to server
                send_sensor_data(user_id, sensor_data)
            # Wait for some time before sending next data (e.g., every 5 seconds)
            time.sleep(900)
    except KeyboardInterrupt:
        print("Simulation stopped by user.")
    """
