# Agriculture Monitoring System

This folder contains a collection of Python scripts designed for monitoring agricultural conditions using sensors and visualizing the data. The system comprises three main components:

- **server.py**: Flask-based server for receiving and storing sensor data.
- **sensor.py**: Simulates sensor data generation and sends it to the server.
- **client.py**: Retrieves sensor data from the server, visualizes it, and allows user interaction.

## Dependencies

- Python 3.x
- Flask
- Requests
- Matplotlib

## Server

Example on how the server code operates. You don't need to worry about this unless you want to try it yourself :)

## Client

This sript can also act as a library for all the functions one needs to access the data in the main flask server, which is host in: http://84.90.102.75:59000.

### Instructions

1. Execute the script (python3 client.py),
2. Login or register as new user, if you want to login to an already existing database use thre credentials "filipe" and "pass" as name and password,
3. A list will appear with all the nodes available in the database, choose one (by writing it down),
4. Enter the number of days you want to view the data, e.g. view the data of the last 3 days.
5. A page will appear with all the plots and the stdout will print the last battery voltage value of the choosen node,
6. Repeat ;)

As of now (24/03/2024) the data displayed in the "filipe" database is simulated using a virtual sensor.

## Info

If you wish to run the server yourself, change the SERVER_URL varible in both the client.py and sensor.py script
