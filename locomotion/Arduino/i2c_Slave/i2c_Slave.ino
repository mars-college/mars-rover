// Simple Sketch for ATtiny85
// Listens to I2C for an 8-bit value
// writes that value to PWM output

#include <TinyWireS.h>
#include <usiTwiSlave.h>

#define PWM_PIN 1 // pin #6 on the ATtiny85
#define ZONE_ID 10 // 10 is motor A, 20 is motor B

float ease_rate = 0.125;
float value;
int target;

//////////////////////////////////////////////////////////////////////////////

void setup() {

  //  warning: this contains cryptic register settings for the ATTiny85 timers

  cli(); // clear interrupts
  // timer0 PWM freqeuncy ~8Khz (16Mhz / 256 / 8)
  TCCR0A = 0b00000011; // waveform generation mode (WGM) = fast pwm
  TCCR0B = 0b00000010; // bits 0-2 are prescaler /8

  // timer1 frequency ~ 60Hz ( 16Mhz / 8192 / 60 ~ 32.5 )
  TCCR1 = 0b10001110; //CTC - 16Mhz / 8192
  OCR1A = 0b00000000; //interrupt when the clock is reset
  OCR1C = 0b00010000; //clock is reset when it hits 32
  TIMSK = 0b01000000; // attach interrupt to OCR1A
  sei(); // set interrupts

  pinMode(PWM_PIN, OUTPUT);

  value = 0;
  target = 0;

  TinyWireS.begin(byte(ZONE_ID)); // join i2c bus

}

//////////////////////////////////////////////////////////////////////////////

void loop() {

  while (TinyWireS.available()) {
    target = int(TinyWireS.receive());
  }

  analogWrite(PWM_PIN, value);
}

ISR(TIM1_COMPA_vect) {
  value += ease(value, target, ease_rate);
}

//////////////////////////////////////////////////////////////////////////////

float ease(float _val, int _target, float _ease) {
  return ( float(_target) - _val ) * _ease;
}
