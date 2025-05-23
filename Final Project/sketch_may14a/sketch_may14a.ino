#include <SPI.h>
#include <MFRC522.h>
#include <WiFiNINA.h>
#include <PubSubClient.h>
#include <Servo.h>

// HiveMQ Cloud credentials
#define MQTT_USER "hivemq.webclient.1747639899064"
#define MQTT_PASS "8961ABCDbedfEGah,%<$"

// WiFi credentials
#define WIFI_SSID "A"
#define WIFI_PASSWORD "12345678"

// MQTT details
#define MQTT_SERVER "484e831498dc44a1a9ba35c92a683dca.s1.eu.hivemq.cloud"
#define MQTT_PORT 8883
#define MQTT_CLIENT_ID "arduinoClient-RFID-Feeder"
#define MQTT_PUBLISH_TOPIC "rfid/card_scans"
#define MQTT_SUBSCRIBE_TOPIC "feed/time"

// rfid reader pins
const int SS_PIN = 10;
const int RST_PIN = 9;

// Servo pin
const int servoPin = 3;
Servo myServo;

// the rfid readerr
MFRC522 mfrc522(SS_PIN, RST_PIN);

// wifi and mqtt
WiFiSSLClient wifiClient;
PubSubClient client(wifiClient);

// function to read the RFID card ID and return it as a String
String readRFIDCardId() {
  if (mfrc522.PICC_IsNewCardPresent()) {
    if (mfrc522.PICC_ReadCardSerial()) {
      String cardId = "";
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        if (mfrc522.uid.uidByte[i] < 0x10) {
          cardId += "0";
        }
        cardId += String(mfrc522.uid.uidByte[i], HEX);
      }
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
      return cardId;
    }
  }
  // no card read
  return "";
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  if (strcmp(topic, MQTT_SUBSCRIBE_TOPIC) == 0) {
    String payloadStr = "";
    for (int i = 0; i < length; i++) {
      payloadStr += (char)payload[i];
    }

    feed(payloadStr.toInt());  // feed
  }
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void mqtt_connect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT broker with SSL...");
    if (client.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS)) {
      Serial.println("connected");
      client.subscribe(MQTT_SUBSCRIBE_TOPIC);
      Serial.print("Subscribed to topic: ");
      Serial.println(MQTT_SUBSCRIBE_TOPIC);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void feed(int feedTime) {
  Serial.print("Feeding duration received: ");
  Serial.print(feedTime);
  Serial.println(" seconds");

  myServo.write(90);
  delay(feedTime * 1000);
  myServo.write(0);
}


void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();

  myServo.attach(servoPin);
  myServo.write(0);

  setup_wifi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
  client.setCallback(callback);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Attempting to reconnect...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
      Serial.print(".");
    }
    Serial.println("\nWiFi reconnected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  }

  if (!client.connected()) {
    mqtt_connect();
  }
  client.loop();


  String cardId = readRFIDCardId();
  if (cardId != "") {
    Serial.print(F("Card UID scanned: "));
    Serial.println(cardId);
    client.publish(MQTT_PUBLISH_TOPIC, cardId.c_str());
    Serial.print(F("Published card UID to MQTT topic (SSL): "));
    Serial.println(MQTT_PUBLISH_TOPIC);

    // prevents double reading
    delay(1000);
  }
  delay(50);
}