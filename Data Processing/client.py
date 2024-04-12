import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime
import requests
import csv

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

def plot_sensor_data(sensor_data):
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
    print(f"Last vbat value: {last_vbat} V")

    plt.show()

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
        else:
            print("Failed to get node list. Status code:", response.status_code)
    except Exception as e:
        print("Exception occurred while getting node list:", e)

# Function to get sensor data from the server
def get_sensor_data(user_id, node_id, days):
    try:
        # Construct URL for the endpoint to retrieve measurements for a specific node for the last N days
        url = f'{SERVER_URL}/measurements/{node_id}/{days}'
        # Set Authorization header with user ID
        headers = {'Authorization': user_id}
        # Send GET request to server
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"Data for node '{node_id}' for the last {days} days:")
            return data
        else:
            print("Failed to get data. Status code:", response.status_code)
    except Exception as e:
        print("Exception occurred while getting data:", e)

if __name__ == '__main__':
    # Register or login
    choice = input("Register (R) or Login (L): ").lower()
    if choice == 'r':
        name = input("Enter your name: ")
        password = input("Enter your password: ")
        user_id = register_user(name, password)
    elif choice == 'l':
        name = input("Enter your name: ")
        password = input("Enter your password: ")
        user_id = login(name, password)

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