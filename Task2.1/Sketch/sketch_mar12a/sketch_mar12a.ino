#include <DHT22.h>
#include <WiFiNINA.h>
#include "secrets.h"
#include "ThingSpeak.h"

#define pinDATA 12 // SDA, or almost any other I/O pin
// write key
// AFTZYV1LWP2UU5YT
// read key
// UYHK6CF1GAYBPZ10

char ssid[] = SECRET_SSID;   // your network SSID (name) 
char pass[] = SECRET_PASS;   // your network password
WiFiClient  client;

unsigned long myChannelNumber = SECRET_CH_ID;
const char * myWriteAPIKey = SECRET_WRITE_APIKEY;

DHT22 dht22(pinDATA); 
 
void setup() {
  Serial.begin(115200); //1bit=10µs
  Serial.println("Yippi");
  ThingSpeak.begin(client);
}

void loop() {

  float t = dht22.getTemperature();
  float h = dht22.getHumidity();

  if (dht22.getLastError() != dht22.OK) {
    Serial.print("last error :");
    Serial.println(dht22.getLastError());
  }

  if(WiFi.status() != WL_CONNECTED){
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(SECRET_SSID);
    while(WiFi.status() != WL_CONNECTED){
      WiFi.begin(ssid, pass);  // Connect to WPA/WPA2 network. Change this line if using open or WEP network
      Serial.print(".");
      delay(5000);     
    } 
    Serial.println("\nConnected.");
  }

  ThingSpeak.setField(1,t);
  ThingSpeak.setField(2,h);

  int x = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);
  if(x == 200){
    Serial.println("Channel update successful.");
  }
  else{
    Serial.println("Problem updating channel. HTTP error code " + String(x));
  }

  Serial.print("h=");Serial.print(h,1);Serial.print("\t");
  Serial.print("t=");Serial.println(t,1);
  delay(60*1000); //Collecting period should be : >1.7 second
}
