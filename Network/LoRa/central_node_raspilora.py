

"""
https://github.com/martynwheeler/raspi-lora


First install GPIO library compatible with raspberry pi 5: $ pip install rpi-lgpio
For broadcasting, send to address 255

Wiring (RFM95 <-> Raspberry Pi 5):
3.3V <-> 3.3V
GND <-> GND
MISO <-> MISO
MOSI <-> MOSI
SCK <-> SCK
NSS <-> GPIO8 (CE0)
RESET <-> !!!!! DON'T CONNECT, CAUSES FAILURE !!!!
DIO0 <-> GPIO5 (can be changed in the code)
"""

from raspi_lora import LoRa, ModemConfig
import time, re

# If after TIMEOUT a node doesn't report back we consider it lost/shutdown
TIMEOUT = 60 #seconds
test = 0

class DeviceManager:
    def __init__(self, timeout):
        self.device_ids = {}
        self.timeout = timeout  # Time in seconds after which a device is considered inactive
        self.available_ids = set(range(2, 245))  # Initialize available IDs
        
    def register_device(self, device_id):
        self.device_ids[device_id] = time.time()  # Store the current time as the last communication time
        self.available_ids.discard(device_id)  # Remove the ID from available IDs
        
    def check_activity(self):
        current_time = time.time()
        for device_id, last_communication_time in list(self.device_ids.items()):
            if current_time - last_communication_time > self.timeout:
                del self.device_ids[device_id]  # Remove the device ID if it's inactive
                print("\nID: " + str(device_id) + " available\n")
                self.available_ids.add(device_id)  # Make the ID available again
                
    def get_available_id(self):
        # Check for inactive devices before assigning a new ID
        self.check_activity()
        
        if self.available_ids:
            new_id = self.available_ids.pop()  # Pop an available ID from the set
        else:
            new_id = None  # No available IDs within the range
        
        if new_id is not None:
            # Register the new device with the current time
            self.register_device(new_id)
        return new_id
    
    def reset_timer(self, device_id): # If device is still alive before the timeout
        if device_id in self.device_ids:
            self.device_ids[device_id] = time.time()  # Update the last communication time for the specified device ID
        else:
            print("Device ID {} not found.".format(device_id))
            self.register_device(device_id)



CENTRAL_NODE_ADDRESS = 1
device_manager = DeviceManager(timeout=TIMEOUT)

def send_to(message, destination_id):
    lora.send(message, destination_id)
    print("[INFO] Sending: " + message)
    lora.set_mode_rx()

# Callback function for received messages (only to this address, or broadcast)
def on_recv(payload):
    global test
    print("\n[INFO] From:", payload.header_from)
    message = payload.message.decode("utf-8") # Aqui pode ser melhorado para verificar se a decodificação falhou e não enviar ACK
    print("\tReceived:", message)
    print("\tRSSI: {}; SNR: {}".format(payload.rssi, payload.snr))

    if "HELLO" in message:
        pattern = r"HELLO-(\w+)"
        match = re.match(pattern, message)
        print("[INFO] Hello " + match.group(1))
        new_id = device_manager.get_available_id()
        send_to("HELLO-" + match.group(1) + "-" + str(new_id), payload.header_from)
    elif "Test" in message:
        test += 1
        if (test % 9) == 0:
            send_to("OK-L", payload.header_from)
            device_manager.reset_timer(payload.header_from)
        else:
            send_to("OK", payload.header_from)
            device_manager.reset_timer(payload.header_from)
    else:
        arr = message.split("-")
        print("\tFrom: " + arr[0])
        print("\t  * Temp: " + arr[1] + "ºC")
        print("\t  * Hum: " + arr[2] + "%")
        print("\t  * Lumisity: " + arr[3] + "%")
        print("\t  * Soil: " + arr[4] + "%")
        send_to("OK", payload.header_from)
        device_manager.reset_timer(payload.header_from)

# Use chip select 0 (CE0). GPIO pin 5 will be used for interrupts
# The address of this device is CENTRAL_NODE_ADDRESS
lora = LoRa(0, 5, CENTRAL_NODE_ADDRESS, freq=868, modem_config=ModemConfig.Bw125Cr45Sf128, tx_power=14, acks=True, crypto=None)
lora.on_recv = on_recv

lora.set_mode_rx() # Set the module to receive mode

# Keep the program running to receive messages
try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nExiting...")

# Deactivate the module
lora.close()
