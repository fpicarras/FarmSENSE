

# Central node (Linux or Windows machine)
# Code for BLE client


import asyncio
from bleak import BleakScanner, BleakClient, BleakError

service_uuid = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
ack_characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a9"


async def connect_to_device(dev):
    try:
        async with BleakClient(dev.address) as client:
            svc = client.services.get_service(service_uuid)
            ch = svc.get_characteristic(characteristic_uuid)
            ack_ch = svc.get_characteristic(ack_characteristic_uuid)

            try:
                data = await client.read_gatt_char(ch)
                data_string = data.decode('utf-8')
                print(data_string)
            except Exception as e:
                print(f"Error reading data: {e}")

            try:
                ack_written = await client.write_gatt_char(ack_ch, bytearray("ACK", "utf-8"))
                print("ACK sent successfully")
            except Exception as e:
                print(f"Error writing ACK: {e}")

    except BleakError as e:
        print(f"Failed to connect to device {dev.address}: {e}")




async def run():
    devices = await BleakScanner.discover()

    if not devices:
        print("No Bluetooth devices found.")
        return

    for dev in devices:
        device_name = dev.name
        if device_name is not None and device_name.startswith("ESP32_NODE"):
            print(f"Device {dev.address} ({dev.name}), RSSI={dev.rssi} dB")
            try:
                await asyncio.wait_for(connect_to_device(dev), timeout=10.0) # The connection has a timeout
            except asyncio.TimeoutError:
                print(f"Timeout while trying to connect to {dev.address}. Moving on to next device.")
                continue

    print("Scanning for devices...")
    #await asyncio.sleep(2)



# Run forever
while True:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

