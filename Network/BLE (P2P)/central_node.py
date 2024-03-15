
# Code for windows machine

import asyncio
from bleak import BleakScanner, BleakClient

service_uuid = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
ack_characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a9"


async def run():
    devices = await BleakScanner.discover()

    if not devices:  # Check if any devices were found
        print("No Bluetooth devices found.")
        return

    for dev in devices:
        device_name = dev.name
        if device_name is not None and device_name.startswith("ESP32_Node"):
            print(f"Device {dev.address} ({dev.name}), RSSI={dev.rssi} dB")

            async with BleakClient(dev.address) as client:
                try:
                    svc = client.services.get_service(service_uuid)
                    ch = svc.get_characteristic(characteristic_uuid)
                    ack_ch = svc.get_characteristic(ack_characteristic_uuid)  # Get the ACK characteristic

                    try:  # Handle potential error during data reading
                        data = await client.read_gatt_char(ch)
                        data_string = data.decode('utf-8')
                        print("Sensor data:", data_string)
                    except Exception as e:
                        print(f"Error reading data: {e}")

                    try:
                        ack_written = await client.write_gatt_char(ack_ch, bytearray("ACK", "utf-8"))  # Write to the ACK characteristic
                        if ack_written:
                            print("Acknowledgement sent successfully")
                        else:
                            print("Failed to send acknowledgement!")
                            # Handle the failure, e.g., log the error or retry with a delay
                    except Exception as e:
                        print(f"Error writing ACK: {e}")
                        # Handle the exception, e.g., log the error or attempt to reconnect

                except Exception as e:  # Catch potential connection errors
                    print(f"Connection error: {e}")

    print("No more devices found. Reconnecting...")
    await asyncio.sleep(2)  # Wait 2 seconds before retrying


while True:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

