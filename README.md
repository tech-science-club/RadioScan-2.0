# RadioScan-2.0
Radiation detector based on Arduino platform + Python Kivy FrameWork

This app is extended modification of previous App RadioScan. New features are:
- arduino Mega 2560 board as main board
- esp 8266 Node mcu as wifi shield
- gps Neo6v2 module to record gps data of place where mesurements are bieng taken.

Main idea to use Arduino Mega 2560 board was to use its wide possibilities to interact with 4 hardware serial communication. 
connection with esp 8266 was established via I2C protocol and wire.h library. 
Esp 8266 was asigned as master, atmega 2560 as slave. Slave's task is to take data from sensors, send it in pakages to master. 
master takes data from pakege, count detected events of registered particles and sent relevant data of events number, t and gps to web server.
Using awardspace.net possibilities we post our data into web table and simultaniously fill in database. having web page with data it is so easy to treat, 
extract data as we wish with Python aroachments. 
 
Main dificulties were to make boards work together. But these were overcome. 

Hardware parts:
dht11 temperature sensor
bluetooth HC-05
Arduino Geiger counter kit with J305 tube.
Arduino Mega 2560
ESP8266 Node mcu
GPS neo6v2 sensor


There are available 4 screens in Python App:
-real time measurement
-real time activity in plot mode
-reaching data from databese and build plot with information within desirable scopes
-inbuild map with relevant position of RadioScan device


It is my first progect, so don't balme me so hard :D



Screen 1

![Screen_1](https://github.com/techmadman/RadioScan-2.0/assets/130900888/dfe6584a-280d-49fe-818d-13ac8b504822)


Screen 2

![Screen_2](https://github.com/techmadman/RadioScan-2.0/assets/130900888/3f3ee40b-7056-412a-848d-80bf6ca59cbc)

Screen 3

![Screen_3](https://github.com/techmadman/RadioScan-2.0/assets/130900888/84956186-d10b-4cb5-ba2f-dcecb404d141)

Screen 4

![Screen_4](https://github.com/techmadman/RadioScan-2.0/assets/130900888/2c3a38db-15b6-418c-a160-cf782b9e73d7)

Working circuit

![Radioscan2 0](https://github.com/techmadman/RadioScan-2.0/assets/130900888/3055053e-b350-4bd5-b58b-30c1cda79114)




