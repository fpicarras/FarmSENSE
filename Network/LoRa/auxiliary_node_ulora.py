


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


AUXILIARY_NODE_ADDRESS = 2  # EDIT for each auxiliary node


# Lora Parameters
RFM95_RST = 43
RFM95_SPIBUS = (1, 7, 9, 8)  # (channel, sck, mosi, miso)
RFM95_CS = 44
RFM95_INT = 6
RF95_FREQ = 868.0 # MHz
RF95_POW = 20 # dBm
CENTRAL_NODE_ADDRESS = 1

# Initialize LoRa
lora = LoRa(RFM95_SPIBUS, RFM95_INT, AUXILIARY_NODE_ADDRESS, RFM95_CS,
            reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=True)


counter = 1

# Loop and send data ----- FOR TESTING (to edit) -----
while True:
    message = "Test message " + str(counter)
    sent = lora.send_to_wait(message, CENTRAL_NODE_ADDRESS, retries=3) # Waits for an ACK (up to 3 retries). Returns True if an ACK was received
    print("Message sent: ", message)
    if sent:
        print ("ACK received")
    else:
        print ("No ACK received, message discarded")
    counter +=1
    sleep(4)