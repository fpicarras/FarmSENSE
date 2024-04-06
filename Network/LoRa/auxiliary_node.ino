
// ESP32 auxiliary node
// LoRa communication



#include <SPI.h>
#include <LoRa.h>

// Define the GPIO pins used by the LoRa transceiver module
#define ss 6
#define rst 43
#define dio0 44

#define NODE_ID 1 // Edit for each node



void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  while (!Serial);

  // Setup LoRa transceiver module
  LoRa.setPins(ss, rst, dio0);
  // Start LoRa for frequency 866 MHz (default in Europe)
  while (!LoRa.begin(868E6)) {
    Serial.print(". ");
    delay(500);
  }
  // Define the sync word (0xF1) to match the receiver. Ranges from 0-0xFF
  LoRa.setSyncWord(0xF1);
  Serial.println("LoRa initialization successful!");
}




/**
 * @brief Sends a message via LoRa (up to 3 attempts) and waits for an acknowledgment (ACK).
 * 
 * @param message The message to be sent. Format is "NODE <node_id>: <message>"
 * @return int Returns 1 if an ACK is received, otherwise returns 0.
 */
int sendDataLora(String message) {
  int maxRetries = 3;
  int retries = 0;
  bool ackReceived = false;

  String nodeMessage = "NODE " + String(NODE_ID) + ": " + message;
  String expectedAck = "ACK " + String(NODE_ID);

  while (retries < maxRetries && !ackReceived) {
    Serial.print("Sending packet: ");
    Serial.println(nodeMessage);

    // Send LoRa packet to receiver
    LoRa.beginPacket();
    LoRa.print(nodeMessage);
    LoRa.endPacket();

    // Wait for ACK
    delay(2000); // Wait for 2 seconds to receive the ACK
    while (LoRa.available()) {
      String receivedMessage = LoRa.readString();
      if (receivedMessage == expectedAck) {
        ackReceived = true;
        break;
      }
    }

    retries++;
    delay(random(1000, 3000)); // Introduce a random delay (1-3 seconds) before each retransmission attempt to avoid collisions
  }

  if (ackReceived) {
    Serial.print("ACK received with RSSI ");
    Serial.println(LoRa.packetRssi()); // Print RSSI for testing purposes
    return 1;
  } else {
    Serial.println("No ACK received");
    return 0;
  }
}





void loop() {

  // Periodic sensor data collection ...


  sendDataLora(message); // To edit
  delay(4000);
}
