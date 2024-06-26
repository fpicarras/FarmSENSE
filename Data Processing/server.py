from flask import Flask, request, jsonify, send_file
import sqlite3
from datetime import datetime, timedelta
import threading
import uuid
import hashlib
import numpy as np
import cv2
import json

from img_funcs import predict, files, lux_prevision

app = Flask(__name__)

"""
CLIENT RELATED
"""

# Function to create a SQLite connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to create a table to store user credentials if it doesn't exist
def create_users_table(conn):
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

# Function to insert user credentials into the database
def add_user(conn, name, password):
    user_id = str(uuid.uuid4().hex)[:16]  # Generate a unique user_id
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash the password
    insert_sql = """
        INSERT INTO users (id, name, password)
        VALUES (?, ?, ?)
    """
    try:
        c = conn.cursor()
        c.execute(insert_sql, (user_id, name, hashed_password))
        conn.commit()
        return user_id
    except sqlite3.Error as e:
        print(e)
        return None

# Function to retrieve user_id based on name and password
def get_user_id(conn, name, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash the password
    select_sql = """
        SELECT id
        FROM users
        WHERE name = ? AND password = ?
    """
    try:
        c = conn.cursor()
        c.execute(select_sql, (name, hashed_password))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            return None
    except sqlite3.Error as e:
        print(e)
        return None

# Route to register a new user
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    name = data.get('name')
    password = data.get('password')
    if not name or not password:
        return 'Name and password are required', 400

    conn = create_connection('users.db')
    with conn:
        create_users_table(conn)
        
        # Check if the name already exists
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE name=?", (name,))
        existing_user = c.fetchone()
        if existing_user:
            return 'User with this name already exists', 409  # Conflict
            
        user_id = add_user(conn, name, password)
        if user_id:
            return jsonify({'user_id': user_id}), 201
        else:
            return 'Failed to register user', 500

# Route to authenticate a user and retrieve user_id
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name')
    password = data.get('password')
    if not name or not password:
        return 'Name and password are required', 400

    conn = create_connection('users.db')
    with conn:
        user_id = get_user_id(conn, name, password)
        if user_id:
            return jsonify({'user_id': user_id}), 200
        else:
            return 'Invalid credentials', 401

"""
NODES RELATED
"""

# Function to create a table to store measurements if it doesn't exist
def create_table(conn):
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            node_id TEXT NOT NULL,
            air_temp REAL NOT NULL,
            air_humidity REAL NOT NULL,
            soil_humidity REAL NOT NULL,
            luminosity REAL NOT NULL,
            vbat REAL NOT NULL,  -- Add vbat column
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

# Function to receive measurements from nodes
def receive_measurements(user_id, data):
    if not user_id:
        return 'Unauthorized', 401
    
    node_id = data.get('node_id')
    air_temp = data.get('air_temp')
    air_humidity = data.get('air_humidity')
    soil_humidity = data.get('soil_humidity')
    luminosity = data.get('luminosity')
    vbat = data.get('vbat')  # Get vbat data

    if None in [node_id, air_temp, air_humidity, soil_humidity, luminosity, vbat]:
        return 'Missing data', 400

    conn = create_connection(f'{user_id}_measurements.db')
    with conn:
        create_table(conn)
        insert_sql = """
            INSERT INTO measurements (user_id, node_id, air_temp, air_humidity, soil_humidity, luminosity, vbat)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        conn.execute(insert_sql, (user_id, node_id, air_temp, air_humidity, soil_humidity, luminosity, vbat))
        return 'Measurement received', 201


# Function to retrieve the list of nodes
def get_nodes(user_id):
    conn = create_connection(f'{user_id}_measurements.db')
    with conn:
        select_sql = """
            SELECT DISTINCT node_id
            FROM measurements
        """
        cursor = conn.execute(select_sql)
        nodes = [row[0] for row in cursor.fetchall()]
        return nodes

# Route to receive measurements from nodes
@app.route('/measurements', methods=['POST'])
def receive_measurements_route():
    data = request.json
    user_id = request.headers.get('Authorization')  # Get user ID from Authorization header
    threading.Thread(target=receive_measurements, args=(user_id, data)).start()
    return 'Measurement received', 201

@app.route('/image', methods = ['POST', 'GET'])
def recieve_image_route():
    user_id = request.headers.get('Authorization')  # Get user ID from Authorization header
    if not user_id:
        return 'Unauthorized', 401
    if request.method == 'POST':
        
        image = request.files['img']

        in_memory_file = image.read()
        np_img = np.frombuffer(in_memory_file, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        predict.detect(img, user_id, 'img_funcs/tomato.pt')
        return 'Measurement received', 201
    elif request.method == 'GET':
        print(request.headers.get('typ'))
        f = files.get_latest_files(user_id, 1, request.headers.get('typ'))
        if f[0] == [] or f[1] == []:
            return "No images under given ID!", 404
        img = f[1][0]
        dict = f[0][0]
        if request.headers.get('opt') == "img":
            return send_file(user_id + "/" + img, mimetype='image/png')
        elif request.headers.get('opt') == "data":
            print(user_id + "/" + dict)
            f = open(user_id + "/" + dict)
            dict = f.read()
            f.close()
            return dict

# Route to retrieve measurements for a specific node for the last N days
@app.route('/measurements/<node_id>/<int:days>', methods=['GET'])
def get_measurements(node_id, days):
    user_id = request.headers.get('Authorization')  # Get user ID from Authorization header
    if not user_id:
        return 'Unauthorized', 401
    
    conn = create_connection(f'{user_id}_measurements.db')
    with conn:
        select_sql = """
            SELECT air_temp, air_humidity, soil_humidity, luminosity, timestamp, vbat
            FROM measurements
            WHERE node_id = ? AND timestamp >= date('now', '-{} days')
        """.format(days)
        cursor = conn.execute(select_sql, (node_id,))
        measurements = cursor.fetchall()
        return jsonify(measurements)

# Route to retrieve the list of nodes
@app.route('/nodes', methods=['GET'])
def get_node_list():
    user_id = request.headers.get('Authorization')  # Get user ID from Authorization header
    if not user_id:
        return 'Unauthorized', 401

    nodes = get_nodes(user_id)
    return jsonify(nodes)

# Get all the last measurements for each node
def get_last_measurments(user_id):
    try:
        conn = create_connection(f'{user_id}_measurements.db')
        with conn:
            cursor = conn.cursor()
            select_sql = """
                SELECT node_id, air_temp, air_humidity, soil_humidity, luminosity, timestamp, vbat
                FROM measurements
                WHERE (node_id, timestamp) IN (
                    SELECT node_id, MAX(timestamp)
                    FROM measurements
                    GROUP BY node_id
                )
            """
            cursor.execute(select_sql)
            measurements = cursor.fetchall()

            data = [
                {
                    'node_id': row[0],
                    'air_temp': row[1],
                    'air_humidity': row[2],
                    'soil_humidity': row[3],
                    'luminosity': row[4],
                    'timestamp': row[5],
                    'vbat': row[6]
                } for row in measurements
            ]

            return data

    except Exception as e:
        return null

# Function to get all the luminosity measurements
def get_luminosity(user_id, days, node):
    ret = []
    try:
        conn = create_connection(f'{user_id}_measurements.db')
        with conn:
            cursor = conn.cursor()
            select_sql = """
                SELECT luminosity
                FROM measurements
                WHERE node_id = ? AND timestamp >= date('now', '-{} days')
            """.format(days)
            cursor.execute(select_sql, (node,))
            measurements = cursor.fetchall()
            for row in measurements:
                ret.append(row[0])
            return ret
    except Exception as e:
        return None
    

@app.route('/status', methods=['GET'])
def get_status():
    
    user_id = request.headers.get('Authorization')  # Get user ID from Authorization header
    if not user_id:
        return 'Unauthorized', 401
    data = get_last_measurments(user_id)
    if data:
        return jsonify(data), 200
    else:
        return 'No data found', 500

@app.route('/prevision', methods=['GET'])
def get_prevision():
    user_id = request.headers.get('Authorization')
    if not user_id:# Get all the measurments for each node
        return 'Unauthorized', 401

    data = get_luminosity(user_id, 10, 'node1')
    if not data:
        return 'No data found...', 500
    
    f = files.get_latest_files(user_id, 1, "tomato")
    if f[0] == [] or f[1] == []:
        return "No images under given ID!", 404
    dict = f[0][0]

    threshold = 2000000
    acquisitions_day = 8
    days_until_threshold, threshold_day = lux_prevision.calculate_acquisitions_until_threshold(data, threshold, acquisitions_day, user_id + "/" + dict, user_id)
    
    return send_file(user_id + "/plot_acumul.png", mimetype='image/png'), 200

if __name__ == '__main__':
    debug = True
    app.run(host='0.0.0.0', port=5000)
