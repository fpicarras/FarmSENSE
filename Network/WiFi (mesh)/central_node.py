# Raspberry Pi node.
# A WiFi network should be configured through the operating system


import socket

# Create a TCP/IP socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = "localhost"
port = 8000

# Bind the socket to a specific address and port
server_sock.bind((server_ip, port))

# Listen for incoming connections
server_sock.listen(4)  # Can have up to 5 (4 in queue) gateway nodes

while True:
    # Wait for a connection
    print('Waiting for a gateway node...')
    connection, client_address = server_sock.accept()

    try:
        print('Connection from', client_address)

        # Create an empty string to store the received data
        received_message = ""

        # Receive data until a newline character is encountered
        while True:
            data = connection.recv(16) # Blocks until data is received
            if not data: # When connection is closed by the client
                print("Error: Connection closed without receiving complete data.")
                break
            received_message += data.decode("utf-8")  # Assuming data is in UTF-8 format

            # Check if the received data contains a newline character
            if "\n" in received_message:
                break

        # Print the entire received message
        print('Received message:', received_message)

        # You can now process or save the received_data as needed

        # Send a response back to the client (optional)
        connection.sendall(b"Message received successfully!")

    finally:
        # Clean up the connection
        connection.close()

