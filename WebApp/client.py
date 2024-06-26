import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime
import requests
import csv
import json

# URL of your Flask server
SERVER_URL = 'http://84.90.102.75:59000'
user_id = None

def register_user(name, password):
    url = f'{SERVER_URL}/register'
    data = {'name': name, 'password': password}
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print("User registered successfully.")
        print("Your user ID is:", response.json()['user_id'])
        return response.json()['user_id']
    else:
        print("Failed to register user. Status code:", response.status_code)
        return None

def login(name, password):
    url = f'{SERVER_URL}/login'
    print("Using:", url)
    data = {'name': name, 'password': password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Login successful.")
        print("Your user ID is:", response.json()['user_id'])
        return response.json()['user_id']
    else:
        print("Failed to login. Status code:", response.status_code)
        return None

# Batt percent
def calculate_battery_percentage(vbat):
    bat_perc = 0.0
    bat_max = 4.2
    bat_min = 3.0

    if vbat > 3.7:
        bat_perc = 80.0 + (vbat - 3.7) / (bat_max - 3.7) * 20.0
    elif 3.5 <= vbat <= 3.7:
        bat_perc = 20.0 + (vbat - 3.5) / 0.2 * 60.0
    else:
        bat_perc = (vbat - bat_min) / (3.5 - bat_min) * 20.0

    bat_perc = max(0.0, min(100.0, bat_perc))
    bat_perc_rounded = round(bat_perc)
    
    return bat_perc_rounded

def plot_sensor_data(sensor_data):
    print(sensor_data)
    timestamps = [datetime.datetime.strptime(measurement[4], '%Y-%m-%d %H:%M:%S') for measurement in sensor_data]
    air_temp = [measurement[0] for measurement in sensor_data]
    air_humidity = [measurement[1] for measurement in sensor_data]
    soil_humidity = [measurement[2] for measurement in sensor_data]
    luminosity = [measurement[3] for measurement in sensor_data]

    # Plotting
    fig, axs = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

    axs[0].plot(timestamps, air_temp, label='Air Temperature', color='tab:red')
    axs[0].set_ylabel('Air Temperature (°C)')
    axs[0].legend()

    axs[1].plot(timestamps, air_humidity, label='Air Humidity', color='tab:blue')
    axs[1].set_ylabel('Air Humidity (%)')
    axs[1].legend()

    axs[2].plot(timestamps, soil_humidity, label='Soil Humidity', color='tab:green')
    axs[2].set_ylabel('Soil Humidity (%)')
    axs[2].legend()

    axs[3].plot(timestamps, luminosity, label='Luminosity', color='tab:orange')
    axs[3].set_ylabel('Luminosity (lux)')
    axs[3].legend()

    plt.xlabel('Timestamp')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Format x-axis ticks as dates
    date_format = DateFormatter('%Y-%m-%d %H:%M:%S')
    axs[3].xaxis.set_major_formatter(date_format)

    # Print the last Battery Voltage value value
    last_vbat = sensor_data[-1][5]
    print(f"Last vbat value: {last_vbat} %")

    bat_perc = calculate_battery_percentage(last_vbat)

    return bat_perc


def save_sensor_data_to_csv(sensor_data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Air Temperature', 'Air Humidity', 'Soil Humidity', 'Luminosity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for measurement in sensor_data:
            writer.writerow({'Timestamp': measurement[4], 'Air Temperature': measurement[0],
                             'Air Humidity': measurement[1], 'Soil Humidity': measurement[2],
                             'Luminosity': measurement[3]})

# Function to get the list of nodes from the server
def get_node_list(user_id):
    try:
        # Construct URL for the endpoint to retrieve the list of nodes
        url = f'{SERVER_URL}/nodes'

        # Set Authorization header with user ID
        headers = {'Authorization': user_id}

        # Send GET request to server
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            node_list = response.json()
            print("List of nodes:")
            for node in node_list:
                print(node)
            return node_list  # Return the node list
        else:
            print("Failed to get node list. Status code:", response.status_code)
            return []  # Return an empty list if request fails
    except Exception as e:
        print("Exception occurred while getting node list:", e)
        return []  # Return an empty list if exception occurs


def compresion(data, level):
    """
    level:
        1 -> no compression
        2 -> two points per day
        4 -> 4 points/day
        6 -> 6 points/day
        ...
        24 = 1
    """
    new_data = []
    spaces = 24/level
    i = 0
    for entry in data:
        hour = float(entry[4][11:13])+float(entry[4][14:16])/60
        if hour > i and hour <= i + spaces:
            new_data.append(entry)
            i += spaces
            i %= 24
    return new_data

# Function to get sensor data from the server
def get_sensor_data(user_id, node_id, days):
    print(node_id)
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/measurements/{node_id}/{days}'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id}
        # Send GET request to server
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if days == 365:
                data = compresion(data, 2)
            elif days == 28:
                data = compresion(data, 4)
            elif days == 7:
                data = compresion(data, 8)
            return data
        else:
            print("Failed to get data. Status code:", response.status_code)
    except Exception as e:
        print("Exception occurred while getting data:", e)

def check_node_status(node):
    messages = []
    id = node["node_id"]

    # Para já o broken não está a ser utilizado nas notificações
    if id.lower() == "broken":
        return messages

    if calculate_battery_percentage(node["vbat"]) < 20:
        messages.append(id + " Low battery! - " + str(calculate_battery_percentage(node["vbat"])) + "%")
    if node["soil_humidity"] >= 80:
        messages.append(id + " Flooded soil! - " + str(node["soil_humidity"]) + "%")
    elif node["soil_humidity"] < 60:
        messages.append(id + " Dry soil! - " + str(node["soil_humidity"]) + "%")
    if node["air_humidity"] >= 75:
        messages.append(id + " High humidity! - " + str(node["air_humidity"]) + "%")
    elif node["air_humidity"] < 50:
        messages.append(id + " Low humidity! - " + str(node["air_humidity"]) + "%")
    if node["air_temp"] >= 28:
        messages.append(id + " High temperatures! - " + str(node["air_temp"]) + "ºC")
    elif node["air_temp"] < 24:
        messages.append(id + " Low temperatures! - " + str(node["air_temp"]) + "ºC")
    return messages

# Returns a list of strings with all the notifications from the nodes
def get_status(user_id):
    messages = []
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/status'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id}
        # Send GET request to server
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for node in data:
                messages += check_node_status(node)
            return messages
        else:
            print("Failed to get data. Status code:", response.status_code)
    except Exception as e:
        print("Exception occurred while getting data:", e)

# Returns a list of strings with all the notifications from the nodes
def get_current_status(user_id):
    messages = []
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/status'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id}
        # Send GET request to server
        response = requests.get(url, headers=headers)
        data = response.json()
        for item in data:
            if 'vbat' in item:
                item['vbat'] = calculate_battery_percentage(item['vbat'])
        return data
    except Exception as e:
        print("Exception occurred while getting data:", e)

def get_image(user_id, output_name):
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/image'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id, 'opt': "img", 'typ': "tomato"}
        # Attempt to get image
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(output_name, 'wb') as f:
                f.write(response.content)
        else:
            print("Failed to get data. Status code:", response.status_code)
            return
        # Attempt to get image data
        headers = {'Authorization': user_id, 'opt': "data", 'typ': "tomato"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            print("Failed to get data. Status code:", response.status_code)
            return
    except Exception as e:
        print("Exception occurred while getting data:", e)    


# Get disease image
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

# Function to get prevision of light accumulation
def get_prevision(user_id, output_name):
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/prevision'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id}
        # Send GET request to server
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(output_name, 'wb') as f:
                f.write(response.content)
        else:
            print("Failed to get data. Status code:", response.status_code)
    except Exception as e:
        print("Exception occurred while getting data:", e)

# Function to get plantation data
# Recieves as an argument an opt that accesses said data
def getData(user_id, opt):
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/plantation'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id, 'opt': opt}
        # Send GET request to server
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content.decode('utf-8')
        else:
            print("Failed to get data. Status code:", response.status_code)
    except Exception as e:
        print("Exception occurred while getting data:", e)

# Function to set plantation data to the server
def setData(user_id, opt, data):
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/plantation'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id, 'opt': opt}
        # Send POST request to server
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print("Data sent successfully")
        else:
            print("Failed to send data. Status code:", response.status_code)
    except Exception as e:
        print("Exception occurred while sending data:", e)

if __name__ == '__main__':
    # Register or login
    '''
    choice = input("Register (R) or Login (L): ").lower()
    if choice == 'r':
        name = input("Enter your name: ")
        password = input("Enter your password: ")
        user_id = register_user(name, password)
    elif choice == 'l':
        name = input("Enter your name: ")
        password = input("Enter your password: ")
        user_id = login(name, password)
    '''
    user_id = login('filipe', 'pass')

    if user_id:
        # Proceed with your application using the obtained user_id
        try:
            while True:
                get_node_list(user_id)
                # Prompt user to input node ID and number of days
                node_id = input("Enter node ID: ")
                days = int(input("Enter number of days: "))
                # Call function to get sensor data
                data = get_sensor_data(user_id, node_id, days)
                if bool(data):
                    plot_sensor_data(data)
                    #save_sensor_data_to_csv(data, f"{name}-{node_id}.csv")
                
        except ValueError:
            print("Please enter a valid number of days.")
        except KeyboardInterrupt:
            print("Client script stopped by user.")
    else:
        print("Invalid choice.")
