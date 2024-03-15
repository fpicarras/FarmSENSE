

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
BLECharacteristic* pAckCharacteristic = NULL; // New characteristic for the ACK
bool deviceConnected = false;
bool messageReceived = true;
int messageNumber = 0;
int retries = 0;
int maxRetries = 3; // Define maxRetries
unsigned long messageTimestamp = 0; // Timestamp when the message is sent
unsigned long timeout = 10000; // Increased timeout to 10 seconds

#define SERVICE_UUID           "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID_RX "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define CHARACTERISTIC_UUID_ACK "beb5483e-36e1-4688-b7f5-ea07361b26a9" // New UUID for the ACK characteristic



class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
};


class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pAckCharacteristic) {
      std::string value = pAckCharacteristic->getValue();
      if (value == "ACK") {
        messageReceived = true;
      }
    }
};



void setup() {
  Serial.begin(115200);

  BLEDevice::init("ESP32_Node_1");

  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID_RX,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_WRITE  |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );
  
  pAckCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID_ACK,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_WRITE  |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );

  pAckCharacteristic->setCallbacks(new MyCallbacks());

  pService->start();

  pServer->getAdvertising()->start();
}


void loop() {
  if (deviceConnected) {
    Serial.println("Device connected!");
    if (messageReceived) {
      messageNumber++;
      String message = "Message from Node 1: " + String(messageNumber);
      Serial.println("Message " + String(messageNumber) + " sent, waiting acknowledgment");
      pCharacteristic->setValue(message.c_str());
      pCharacteristic->notify();
      messageReceived = false;
      retries = 0;  // Reset retries on successful message sent
      messageTimestamp = millis(); // Save the timestamp when the message is sent
    } else if (millis() - messageTimestamp > timeout) { // Check for timeout
      if (retries < maxRetries) {
        Serial.println("Message not acknowledged, resending...");
        pCharacteristic->setValue(message.c_str());
        pCharacteristic->notify();
        messageTimestamp = millis(); // Update the timestamp
        retries++;
      } else {
        Serial.println("Maximum retries reached, giving up on message");
        // Handle the case where retries are exhausted (optional)
        }
    }
  } else {
    Serial.println("No device connected!");
  }
  
  delay(2000); // Reduced delay for faster reconnection attempts
}
