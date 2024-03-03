
// Esp32 auxiliary node. Responsible for collecting and sending sensor data periodically.

#include <painlessMesh.h>

#define   MESH_SSID       "meshNetwork"
#define   MESH_PASSWORD   "meshPassword"
#define   MESH_PORT       5555

Scheduler userScheduler; 
painlessMesh  mesh;



// Needed for painless library
void receivedCallback(uint32_t from, String &msg ) {
  Serial.printf("Received from %u msg=%s\n", from, msg.c_str());
}

void newConnectionCallback(uint32_t nodeId) {
    Serial.printf("New Connection, nodeId = %u\n", nodeId);
}

void changedConnectionCallback() {
  Serial.printf("Changed connections\n");
}

void nodeTimeAdjustedCallback(int32_t offset) {
    Serial.printf("Adjusted time %u. Offset = %d\n", mesh.getNodeTime(),offset);
}


// Measuring each 5 seconds
Task taskMeasureData( TASK_SECOND * 5 , TASK_FOREVER, &measureData );


// Change for periodic measuring and sending data. Can be altered to send the message to a specific node (more complex).
void measureData() {
  String msg = "Sensor data: \n"; // \n message termination

  msg += readSensor(); // Assume readSensor() is a function that reads sensor data

  mesh.sendBroadcast(msg); // Message is broadcasted
  Serial.printf("Sent message: %s\n", msg.c_str()); // Debugging 
}



void setup() {
  Serial.begin(115200);

  mesh.setDebugMsgTypes(ERROR | STARTUP);  
  mesh.init(MESH_SSID, MESH_PASSWORD, &userScheduler, MESH_PORT);
  mesh.onReceive(&receivedCallback);
  mesh.onNewConnection(&newConnectionCallback);
  mesh.onChangedConnections(&changedConnectionCallback);
  mesh.onNodeTimeAdjusted(&nodeTimeAdjustedCallback);

  userScheduler.addTask(taskMeasureData); // Adds the taskMeasureData task to the scheduler.
  taskMeasureData.enable(); // Enables the taskMeasureData task, allowing it to run.
}



void loop() {
  mesh.update();
}

