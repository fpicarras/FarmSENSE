
// Esp32 gateway node. Responsible for receiving data from other auxiliary nodes and sending it to the central node.
// Other gateway nodes can be configured.

#include <painlessMesh.h> // Library for mesh network
#include <WiFi.h>

#define   MESH_SSID       "meshNetwork" // MESH_SSID and MESH_PASSWORD should be the same for all nodes in the same mesh network.
#define   MESH_PASSWORD   "meshPassword"
#define   MESH_PORT       5555
#define   WIFI_SSID       "your_SSID"
#define   WIFI_PASSWORD   "your_PASSWORD"
#define   RASPBERRY_PI_IP "192.168.1.100" // Change this to Raspberry Pi's IP address
#define   RASPBERRY_PI_PORT 1234 // Change this to Raspberry Pi's listening port


Scheduler userScheduler; // Used to schedule internal tasks necessary for maintaining the mesh network. Other tasks can be added.
painlessMesh  mesh;
WiFiClient client;



// Needed for painless library
void newConnectionCallback(uint32_t nodeId) {
    Serial.printf("New Connection, nodeId = %u\n", nodeId);
}

void changedConnectionCallback() {
  Serial.printf("Changed connections\n");
}

void nodeTimeAdjustedCallback(int32_t offset) {
    Serial.printf("Adjusted time %u. Offset = %d\n", mesh.getNodeTime(),offset);
}


// Example of function to process received message
void receivedCallback(uint32_t from, String &msg) {
  Serial.printf("Received from %u msg=%s\n", from, msg.c_str()); // Debugging
  sendMessageToRaspberryPi(msg);
}

// Send message to central node with TCP
void sendMessageToRaspberryPi(String message) {
  if (!client.connect(RASPBERRY_PI_IP, RASPBERRY_PI_PORT)) {
    Serial.println("Connection to Raspberry Pi failed");
    return;
  }

  client.print(message);

  Serial.println("Message sent to Raspberry Pi");
}




void setup() {
  Serial.begin(115200); // Start serial communication for debugging purposes. 115200 is the baud rate in bits per second (baud) for serial communication.

  mesh.setDebugMsgTypes(ERROR | STARTUP); // Sets the types of debug messages that the mesh network will output to the serial monitor.
  mesh.init(MESH_SSID, MESH_PASSWORD, &userScheduler, MESH_PORT);
  mesh.onReceive(&receivedCallback); // Sets the function that will be called when a message is received from the mesh network.
 
  
  // Connect to the central node's wifi network
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

}


void loop() {
  mesh.update(); // Update the state of the mesh network
}

