#include <DHT.h>
#include <TinyGPS++.h>

#define DHT11_PIN 2
#define DHTTYPE DHT11
#include <Wire.h>

DHT dht(DHT11_PIN, DHTTYPE);

float Lat = 0.00;
float Long = 0.00;
float temp_data;
String out_line;
String coordinates;


//unsigned long currentMillis = 0, prevMillis = 0, intervalMillis = 1000;

unsigned long previousMillis;
unsigned long previousMillis_2;
unsigned long previousMillis_3;

unsigned long counts = 0;
unsigned long events = 0;

char temp[32];

#define LOG_PERIOD 1000//3600000
#define LOG_PERIOD_2 1000
#define LOG_PERIOD_3 1000


TinyGPSPlus gps;

void  impulse() {
  counts++;
  events++;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial1.begin(9600);
  //Serial2.begin(9600);
  dht.begin();
  //volatile int counts;
  pinMode(3, INPUT);
  attachInterrupt(digitalPinToInterrupt(3), impulse, FALLING);
  
  Wire.begin(8);                // join I2C bus with address #8
  Wire.onRequest(requestEvent); // register event 
  
   
}

void loop() {
  
  coordinate();
  radiation();
  t();
  
  
  String out_line = String(temp_data) + String(":") + String(counts) + String(":") + String(Lat,6) + String("/")+String(Long,6)+ String(":");
  int out_line_length = out_line.length()+1;
  out_line.toCharArray(temp, out_line_length);

  upload_data_to_serial_monitor();
  requestEvent();
  
}
void t(){
  temp_data = dht.readTemperature();
  }  
 
void radiation() {
  unsigned long rad_currentMillis = millis();
  if (rad_currentMillis - previousMillis > LOG_PERIOD) {
    previousMillis = rad_currentMillis;
    counts = 0;  
  }
}

void coordinate(){
  
  while (Serial1.available() > 0) {   // try if (Serial1.available()
    char c = Serial1.read();
    
    //Serial.print(c);
  
   if (gps.encode(c)) {
   // If a new set of valid GPS data is available, print it
     if (gps.location.isValid()) {
        Lat = (gps.location.lat());
      
        Long =(gps.location.lng());
      }
      
     else{
        Lat = 0.00;
        Long =0.00;
          } 
   }
   }  
}

void upload_data_to_serial_monitor() {
  
  
  
  String Coordinates = String(Lat, 6) + " " + String(Long, 6);
  String Radiation = String(events);

  unsigned long rad_currentMillis_2 = millis();
  if (rad_currentMillis_2 - previousMillis_2 > LOG_PERIOD_2) {
    previousMillis_2 = rad_currentMillis_2;
    Serial.print("Temperature: " + String(temp_data) + " ");
    Serial.print("Radiation: " + Radiation + " ");
    Serial.println("coordinates: " + Coordinates);
    events = 0;
  }
 


}   


void requestEvent() {
  
  
  
//  unsigned long rad_currentMillis_3 = millis();
//  if (rad_currentMillis_3 - previousMillis_3 > LOG_PERIOD_3) {
//    previousMillis_3 = rad_currentMillis_3;
    
    Wire.write(temp);
    //Serial.println("Senr data to esp8266: ");
    //Serial.println(temp);
    //Serial.println("-------------");
  //} 
}
