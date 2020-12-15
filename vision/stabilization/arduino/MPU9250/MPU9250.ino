/* Nothing fancy. Listen for requests. Always be polling, transmit the current data
   over serial. Maybe SPI is faster? All depends on Python's SPI libraries and whether
   the Jetson plays nice with the arduino, I guess.
*/

#include "MPU9250.h" // credit: https://github.com/hideakitai/MPU9250
#include <Wire.h> // for i2c

MPU9250 mpu;

uint8_t ADDRESS = 0x68; // default i2c address for the MPU9250
boolean isReady = false;
float r = 0.0;
float p = 0.0;
float y = 0.0;

void sendStatus() {
  Serial.print("{\"status\" : ");
  Serial.print(isReady);
  Serial.print(", \"roll\" : ");
  Serial.print(r);
  Serial.print(", \"pitch\" : ");
  Serial.print(p);
  Serial.print(", \"yaw\" : ");
  Serial.print(y);
  Serial.println("}");
}

void serialEvent() {
  while (Serial.available()) {
    String message = Serial.readStringUntil('\n');
    if (message.equals("fetch")) {
      sendStatus();
    }
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect
  }
  Wire.begin();
  sendStatus();
  mpu.setup(ADDRESS);
  mpu.calibrateAccelGyro();
  mpu.calibrateMag();
  isReady = true;
  sendStatus();
}

void loop() {
  if (mpu.update()) {
    r = mpu.getRoll();
    p = mpu.getPitch();
    y = mpu.getYaw();
  }
}
