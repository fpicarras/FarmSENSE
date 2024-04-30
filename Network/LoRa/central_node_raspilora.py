

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


CENTRAL_NODE_ADDRESS = 1



# Callback function for received messages (only to this address, or broadcast)
def on_recv(payload):
    print("From:", payload.header_from)
    message = payload.message.decode("utf-8") # Aqui pode ser melhorado para verificar se a decodificação falhou e não enviar ACK
    print("Received:", message)
    print("RSSI: {}; SNR: {}".format(payload.rssi, payload.snr))

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
