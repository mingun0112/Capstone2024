#include <ArduinoJson.h>

  

  // Add values in the document
JsonDocument doc;

void setup() {
  // Initialize Serial port
  Serial.begin(115200);
  while (!Serial)
    continue;

  

  doc["A"] = 100;
  doc["B"] = 200;
  doc["C"] = 300;
}
void loop() {
  serializeJson(doc, Serial);
  Serial.println();
  //delay(1000);
}
