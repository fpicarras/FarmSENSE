

# Central Node
# LoRa communication

"""
Wiring chosen (RFM95 - Raspberry Pi):
3.3V - 3.3V
GND - GND
MISO - MISO
MOSI - MOSI
SCK - SCK
NSS - CE1
RESET - GPIO25
DIO0 - Not supported with this library. The interrupt from the RFM95 module is not used,
       adafruit_rfm9x library handles the reception of packets in a polling manner rather than using interrupts.
"""


import time
import board
import busio
import digitalio
import adafruit_rfm9x
import threading

# Define the GPIO pins used by the LoRa transceiver module
NSS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

# Create a SPI object
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create a LoRa object
rfm9x = adafruit_rfm9x.RFM9x(spi, NSS, RESET, 868)

# Define the sync word (0xF1) to match the sender
rfm9x.sync_word = 0xF1


def lora_communication():
    while True:
        packet = rfm9x.receive()
        if packet is not None:
            message = packet.decode("utf-8")
            print("Received: ", message)

            if message.startswith("NODE "): # Check if the message format is correct
                # Extract the sender ID from the message
                sender_id = message.split(" ")[1].split(":")[0]

                # Send an ACK
                ack = "ACK " + sender_id
                rfm9x.send(bytes(ack, "utf-8"))
                print("Sent ACK: ", ack)

        time.sleep(1)




# Create a new thread for the LoRa communication
lora_thread = threading.Thread(target=lora_communication)

# Start the new thread
lora_thread.start()

