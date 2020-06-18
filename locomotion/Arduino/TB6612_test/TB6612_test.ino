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
float dT = 2500.0;
boolean trigger = false;
int output_pins[qty_pins] = { PWMA, PWMB, AIN1, AIN2, BIN1, BIN2 };
int m1_speed_last = 0;
int m2_speed_last = 0;
float progress = 0.0;
uint32_t start_counter = 0;
uint32_t last_counter = 0;
float scale = 0.0;


void setup() {

  Serial.begin(115200);
  // TimerOne Setup
  // for regular sampling of speed
  Timer1.initialize(timer_period); // period in micro seconds (1e5 = 100ms)
  Timer1.attachInterrupt(timerISR);

  for (int i = 0 ; i < sizeof(output_pins) ; ++i) {
    pinMode(i, OUTPUT);
  }

  randomize();
 
}


void loop() {
  
  if (counter - start_counter >= dT) {
    start_counter = counter;
    randomize();
  }

  updateProgress();
  
  analogWrite(PWMA, sin2Scaled(progress));
  analogWrite(PWMB, sin2Scaled(progress));

}

void randomize(){
  randomDirection();
  randomizeSpeed();
  randomizeDuration();
}

void randomizeSpeed() {
  scale = 255.0 * float(random(2500,10000)) / 10000.0;
}
void randomizeDuration(){
  dT = float(random(1000,10000));
}

void randomDirection() {

  if (random(1000) >= 500) {
    m1Reverse();
  } else {
    m1Forward();
  }

  if (random(1000) >= 500) {
    m2Reverse();
  } else {
    m2Forward();
  }

}

void updateProgress() {
  progress = float(counter - start_counter) / dT;
}

void m1Forward() {
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
}

void m2Forward() {
  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, LOW);
}

void m1Reverse() {
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, HIGH);
}

void m2Reverse() {
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, HIGH);
}

//0.0-1.0 = 0.0-PI radians
int sin2Scaled(float angle) {
  float sin2 = pow(sin(angle * PI), 2);
  float scaled = scale * sin2;
  return int(scaled);
}

void timerISR() {
  ++counter;
  
//  if (counter % 250 == 0) {
//    Serial.println("Debug Message: ");
//  }

}
