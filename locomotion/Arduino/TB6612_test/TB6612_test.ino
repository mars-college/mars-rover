#include <TimerOne.h>

#define PWMA 3
#define PWMB 11
#define AIN1 4
#define AIN2 5
#define BIN1 6
#define BIN2 7

const int qty_pins = 6;

uint32_t counter = 0;
uint32_t timer_period = 1000;
float div1 = 1000.0;
float div2 = 1250.0;
int output_pins[qty_pins] = { PWMA, PWMB, AIN1, AIN2, BIN1, BIN2 };

void setup() {

  Serial.begin(115200);

  // TimerOne Setup
  // for regular sampling of speed
  Timer1.initialize(timer_period); // period in micro seconds (1e5 = 100ms)
  Timer1.attachInterrupt(timerISR);

  for (int i = 0 ; i < sizeof(output_pins) ; ++i) {
    pinMode(i, OUTPUT);
  }
}

void loop() {
  analogWrite(PWMA, sinScaled((counter % int(div1) ) / div1));
  analogWrite(PWMB, sinScaled((counter % int(div2) ) / div2));
}

//0-1 = 0-2PI radians
int sinScaled(float angle) {
  return int(map( sin(angle * 2 * PI), -1, 1, 0, 255));
}

void timerISR() {
  ++counter;
  if (counter % timer_period == 0){
  }
}
