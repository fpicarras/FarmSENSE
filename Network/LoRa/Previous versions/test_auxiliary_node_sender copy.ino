

// ESP32 Node: Sender


/*
Wiring (RFM95 <-> Seeed Studio XIAO ESP32S3 Sense):
3.3V <-> 3.3V
GND <-> GND
MISO <-> MISO (D9)
MOSI <-> MOSI (D10)
SCK <-> SCK (D8)
NSS <-> D7 (GPIO44)
RESET <-> D6 (GPIO43)
DI0 <-> D5 (GPIO6)

NSS, RESET, and DI0 can be changed in the code using the correspondent GPIO
*/




#include <SPI.h>
#include <LoRa.h>

// Define the GPIO pins used by the transceiver module
#define ss 44
#define rst 43
#define dio0 6


int counter = 0;

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  while (!Serial);
  Serial.println("LoRa Sender");

  // Setup LoRa transceiver module
  LoRa.setPins(ss, rst, dio0);
  
  // Frequency 868E6 for Europe
  while (!LoRa.begin(868E6)) {
    Serial.println(".");
    delay(500);
  }
  // Change sync word (0xF1) to match the receiver
  // The sync word assures you don't get LoRa messages from other LoRa transceivers
  // ranges from 0-0xFF
  LoRa.setSyncWord(0xF1);
  Serial.println("LoRa Initializing OK!");

}

void loop() {
  Serial.print("Sending packet: ");
  Serial.println(counter);

  //Send LoRa packet to receiver
  LoRa.beginPacket();
  LoRa.print("Hello ");
  LoRa.print(counter);
  LoRa.endPacket();

  counter++;
  delay(4000);
}
