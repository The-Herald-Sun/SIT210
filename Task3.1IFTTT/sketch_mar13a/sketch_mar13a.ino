//
// Pins:
// VCC -> 3.3v or 5v
// GND -> GND
// ADO -> GND or leave disconected
// SDA -> A4
// SCL -> A5

#include "BH1750FVI.h"
#include <WiFiNINA.h>
#include <PubSubClient.h>
#include "secrets.h"

// MQTT Broker
#define MQTT_SERVER "ee7fc5efce6943539590bbc3c2492b1b.s1.eu.hivemq.cloud"
#define MQTT_PORT 8883
#define MQTT_TOPIC "sensor/light"
#define MQTT_USER "hivemq.webclient.1742345157227"  // Replace with your HiveMQ username
#define MQTT_PASSWORD "1D8GV54BYrFwbuxj!,*@"

// wifi things
char ssid[] = "A";
char pass[] = "12345678";
WiFiSSLClient client;


BH1750FVI myLux(0x23);

PubSubClient mqttClient(client);

void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("Connecting to MQTT...");
    if (mqttClient.connect("ArduinoNanoIoT", MQTT_USER, MQTT_PASSWORD)) {
      Serial.println("Connected to MQTT Broker!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.print(__FILE__);
  Serial.println();

  // wifi at it again
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(SECRET_SSID);
    while (WiFi.status() != WL_CONNECTED) {
      WiFi.begin(ssid, pass);  // Connect to WPA/WPA2 network. Change this line if using open or WEP network
      Serial.print(".");
      delay(5000);
    }
    Serial.println("\nConnected.");
  }

  Wire.begin();

  myLux.powerOn();
  myLux.setContLowRes();

  // MQTT
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  // Connect to MQTT
  connectMQTT();
}

void loop() {
  // Get thems Wifis runnin
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(SECRET_SSID);
    while (WiFi.status() != WL_CONNECTED) {
      WiFi.begin(ssid, pass);  // Connect to WPA/WPA2 network. Change this line if using open or WEP network
      Serial.print(".");
      delay(5000);
    }
    Serial.println("\nConnected.");
  }

  float val = myLux.getLux();
  Serial.println(val, 1);

  if (val < 10) {
    mqttClient.publish(MQTT_TOPIC, "ITS DARK PLEASE IM SCARED");
  } else {
    mqttClient.publish(MQTT_TOPIC, "ITS BRIGHT AH MY EYES");
  }
  delay(3000);
}