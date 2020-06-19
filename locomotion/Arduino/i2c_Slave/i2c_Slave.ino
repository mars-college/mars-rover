// Simple Sketch for ATtiny85
// Listens to I2C for an 8-bit value
// writes that value to PWM output

#include <TinyWire.h>

#define ADDRESS 0x40

#define PWM_PIN 1 // pin #6 on the ATtiny85

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

  //  pinMode(PWM_PIN, OUTPUT);

  value = 0;
  target = 0;

  // config TinyWire library for I2C slave functionality
  TinyWire.begin( ADDRESS );
  // sets callback for the event of a slave receive
  //  TinyWire.onReceive( onI2CReceive );

}

//////////////////////////////////////////////////////////////////////////////

void loop() {
  analogWrite(PWM_PIN, 127/*int(value)*/);
}

ISR(TIM1_COMPA_vect) {
  value += ease(value, target, ease_rate);
}

//////////////////////////////////////////////////////////////////////////////

void onI2CReceive(int howMany) {
//   loops, until all received bytes are read
    while(TinyWire.available()>0){
      // toggles the led everytime, when an 'a' is received
//      if(TinyWire.read()=='a') digitalWrite(led_pin, !digitalRead(led_pin));
    }
}

//////////////////////////////////////////////////////////////////////////////

float ease(float _val, int _target, float _ease) {
  return ( float(_target) - _val ) * _ease;
}
