#include <WiFi.h>
#include "ThingSpeak.h"

const char* ssid = "Wokwi-GUEST";          
const char* password = "";                 

WiFiClient client;
unsigned long channelID = 3005560;
const char* writeAPIKey = "ALW22BSTI0HSVEIO";

int ir = 13;
int buzzer = 5;
int lastState = 0;  

void setup() {
  pinMode(ir, INPUT);
  pinMode(buzzer, OUTPUT);
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting...");
    delay(1000);
  }

  Serial.println("Connected to WiFi");
  ThingSpeak.begin(client);
}

void loop() {
  int currentState = digitalRead(ir);

 
  if (currentState == 1 && lastState == 0) {
    Serial.println("Motion Detected!");
    digitalWrite(buzzer, HIGH);

    // Upload to ThingSpeak
    ThingSpeak.setField(1, 1);
    int x = ThingSpeak.writeFields(channelID, writeAPIKey);
    if (x == 200) {
      Serial.println("✅ Data sent to ThingSpeak.");
    } else {
      Serial.print("❌ Failed to send. HTTP error: ");
      Serial.println(x);
    }
  }

  if (currentState == 0) {
    digitalWrite(buzzer, LOW);
  }

  lastState = currentState;  
  delay(100); 
}
