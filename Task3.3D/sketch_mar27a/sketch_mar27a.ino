#include <WiFiNINA.h>
#include <PubSubClient.h>
#include <DHT22.h>

// WiFi things
char ssid[] = "A";
char pass[] = "12345678";
WiFiClient wifiClient;

// MQTT Broker details
#define MQTT_SERVER "broker.emqx.io"
#define MQTT_PORT 1883
#define MQTT_TOPIC "SIT2110/wave"

#define INTERVAL 5000

PubSubClient mqttClient(wifiClient);

// DHT22 Sensor setup
#define DHTPIN 12
DHT22 dht22(DHTPIN);

// #define LED_PIN LED_BUILTIN
#define LED_PIN 11

void connectWifi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting to WiFi: ");
    Serial.println(ssid);
    while (WiFi.status() != WL_CONNECTED) {
      WiFi.begin(ssid, pass);
      Serial.print(".");
      delay(2000);
    }
    Serial.println("\nWiFi Connected!");
  }
}

void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("Connecting to MQTT...");
    if (mqttClient.connect("ArduinoNanoIoT" )) {
      Serial.println("Connected to MQTT Broker!");
      mqttClient.subscribe(MQTT_TOPIC);
    } else {
      Serial.print("MQTT Connection failed. RC=");
      Serial.print(mqttClient.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

// MQTT Callback function - runs when a message is received
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  
  Serial.print("Payload: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  // Flash LED 3 times when a message is received
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(500);
    digitalWrite(LED_PIN, LOW);
    delay(500);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  connectWifi();
  
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(callback);
  
  connectMQTT();
}

int timeStamp = 0;

void loop() {
  connectWifi();
  connectMQTT();
  
  mqttClient.loop();

  // Read humidity
  float humidity = dht22.getHumidity();

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println();

  // Publish humidity if above threshold (e.g., 70%)
  if (humidity > 70.0 && timeStamp - millis() > INTERVAL ) {
    timeStamp = millis();
    mqttClient.publish(MQTT_TOPIC, "Samuel");
    Serial.println("Message Published!");
  }
  delay(3000);
}
