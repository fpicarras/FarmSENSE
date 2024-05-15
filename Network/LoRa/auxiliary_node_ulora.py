


"""
https://github.com/martynwheeler/u-lora

"ulora.py" should be in the same directory as this file

Check ulora.py file for more details on implementation and other functions
For broadcasting, send to address 255

Wiring (RFM95 <-> Seeed Studio XIAO ESP32S3 Sense):
3.3V <-> 3.3V
GND <-> GND
MISO <-> MISO (GPIO8)
MOSI <-> MOSI (GPIO9)
SCK <-> SCK (GPIO7)
NSS <-> D7 (GPIO44)
RESET <-> D6 (GPIO43)
DI0 <-> D5 (GPIO6)

NSS, RESET, and DI0 can be changed in the code using the correspondent GPIO
"""


from time import sleep
from ulora import LoRa, ModemConfig, SPIConfig
import dht

import machine

# Sensor Pins
POWER_PIN = 1
DHT_PIN = 2
LUM_PIN = 3
SOIL_PIN = 4 

# Lora Parameters
RFM95_RST = 43
RFM95_SPIBUS = (1, 7, 9, 8)  # (channel, sck, mosi, miso)
RFM95_CS = 44
RFM95_INT = 6
RF95_FREQ = 868.0 # MHz
RF95_POW = 20 # dBm
CENTRAL_NODE_ADDRESS = 1

AUXILIARY_NODE_ADDRESS = 244  # Initial address for every node
RECIEVED = 0 # Flag to signal if the message send was COMPREHENDED
DEVICE_ID = "tomato" # Unique to each node -> must find a way to config

# Initialize LoRa
lora = LoRa(RFM95_SPIBUS, RFM95_INT, AUXILIARY_NODE_ADDRESS, RFM95_CS,
            reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=True)


counter = 1

# Used to define routines for when the central sends some
# commands in the format: OK-command1-command2- (...) -commandN
def process_command(message):
    commands = message.split("-")[1:]
    for c in commands:
        print("Command: " + c)
        if c[0] == 'L':
            print("TEST COMMAND")
    
# Routine to attempt to send a message, it tries 5 times;
# Returns 1 in case of success ou 0 otherwise;
# It only interpets the message as recieved once RECIEDVED
# is set to 1 -> has to be set in "on_recv" function
def send_to(message, destination_id):
    global RECIEVED
    aux = RECIEVED # Store former message pending flag
    RECIEVED = 0
    sent = 0
    for i in range(5):
        if RECIEVED == 1:
            break
        print("[INFO] Sent: " + message)
        sent = lora.send_to_wait(message, destination_id, retries=3) # Waits for an ACK (up to 3 retries). Returns True if an ACK was received
        if sent:
            print("[INFO] ACK received")
            lora.set_mode_rx()
        else:
            print("[ERROR] No ACK recieved...")
        sleep(1)
    sent = RECIEVED
    RECIEVED = aux
    if not sent:
        print("[ERROR] Failed to get response from central, is it down...?")
    return sent
    
# Function that is executed each time the device recieves a transmition
# (Interrupt handler)
def on_recv(payload):
    global AUXILIARY_NODE_ADDRESS, RECIEVED
    message = payload.message.decode('utf-8')
    print("[INFO] From: " + str(payload.header_from))
    print("\tReceived: " + message)
    print("\tRSSI: {}; SNR: {}".format(payload.rssi, payload.snr))
    if "HELLO" in message:
        if DEVICE_ID in message:
            print("Hello Central!")
            offset = 7 + len(DEVICE_ID)
            AUXILIARY_NODE_ADDRESS = int(message[offset:])
            RECIEVED = 1
            lora.new_addr(AUXILIARY_NODE_ADDRESS)
            print("[INFO] New address: " + str(AUXILIARY_NODE_ADDRESS))
    elif "OK" in message:
        RECIEVED = 1
        if "-" in message:
            # If we have commands...
            process_command(message)
    
lora.on_recv = on_recv

# Routine to establish an id to this device
while True:
    if send_to("HELLO-" + DEVICE_ID, CENTRAL_NODE_ADDRESS):
        break
    else:
        print("\tFailing to get an ID, retrying in 1s...")
        sleep(1)


d = dht.DHT11(machine.Pin(DHT_PIN))
p = machine.Pin(POWER_PIN, machine.Pin.OUT)
lum = machine.ADC(machine.Pin(LUM_PIN, machine.Pin.IN))
lum.atten(machine.ADC.ATTN_11DB)
soil = machine.ADC(machine.Pin(SOIL_PIN, machine.Pin.IN))
soil.atten(machine.ADC.ATTN_11DB)

# Calibration
min_moisture = 3279
max_moisture = 36682 # Possible error point

# Loop and send data ----- FOR TESTING (to edit) -----
while True:
    p.on()
    sleep(2)
    d.measure()
    temp = d.temperature()
    hum = d.humidity()
    moisture = round(100*float(max_moisture - soil.read_u16())/(max_moisture-min_moisture), 2)
    if moisture > 100:
        moisture = 100
    elif moisture < 0:
        moisture = 0
    luminosity = round(100*float(65535-lum.read_u16())/65535, 2)
    
    # message = "Test message " + str(counter) + " : " + str(temp) + "C-"+str(hum)+"%-"+str(luminosity)+"%"
    message = DEVICE_ID + "-" + str(temp) + "-"+str(hum)+"-"+str(luminosity)+"-"+str(moisture)
    
    print(str(moisture) + "% : " + str(soil.read_u16()))
    send_to(message, CENTRAL_NODE_ADDRESS)
    counter +=1
    p.off()
    sleep(1)
    #machine.deepsleep(10000)



