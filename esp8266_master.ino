// esp8266 is set as master device. It recieve slave's sensor data

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

#include <Wire.h>

const char* ssid = "Kviknet-5A55";
const char* password = "7HBXLQWCTQ77NT";
const char* SERVER_NAME = "http://radioscan.atwebpages.com/sensordata.php";
String PROJECT_API_KEY = "************";

#define LOG_PERIOD 3600000

unsigned long previousMillis;


String data; 
String temp;
String rad;
String coord;
int detected_particles;
int radiation;

void setup() {
  Wire.begin();        // join I2C bus (address optional for master)
  Serial.begin(9600);  // start serial for output
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  
}

void loop() {
 
  incom_data();
  post_to_web();
    
}

void post_to_web(){
  
  radiation += rad.toInt();
  
  
  unsigned long rad_currentMillis = millis();
  if (rad_currentMillis - previousMillis > LOG_PERIOD) {
    previousMillis = rad_currentMillis;
    
     
    String temperature_data = "api_key=" + PROJECT_API_KEY;
    temperature_data += "&temperature=" + temp;
    temperature_data += "&radiation=" + String(radiation); // Use the global counts variable
    temperature_data += "&coordinates=" + coord;

    WiFiClient client;
    HTTPClient http;

    http.begin(client, SERVER_NAME);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    int httpResponseCode = http.POST(temperature_data);

    http.end();
    
    Serial.println(radiation);
    Serial.println("**********************");
    
    radiation = 0;
  }
  
  
  }
void incom_data(){
byte n = Wire.requestFrom(8, 32); // Request 26 bytes from the slave device
   // Clear the data string before reading new values
  
  for (int i = 0; i < n; i++) {
    char y = Wire.read();
    data += y;
  }

  //Serial.println(data);

  int delimiterIndex1, delimiterIndex2, delimiterIndex3;
  
  if (delimiterIndex1 != -1 && delimiterIndex2 != -1 && delimiterIndex3 != -1) {
    int delimiterIndex1 = data.indexOf(':');
    temp = data.substring(0, delimiterIndex1);
    data.remove(0, temp.length()+1);
    
    int delimiterIndex2 = data.indexOf(':');
    rad = data.substring(0,delimiterIndex2);
    data.remove(0, rad.length()+1);

    //radiation = rad.toInt();
        
    int delimiterIndex3 = data.indexOf(':');    
    coord = data.substring(0,delimiterIndex3);
    //data.remove(delimiterIndex3, data.length() - (temp.length()+rad.length()+coord.length()+ 3) );

    Serial.println(temp);
    Serial.println(rad);
    Serial.println(coord);
    Serial.println("=========================");
  }
  data = "";
  delay(1000);  
  
  
  }
