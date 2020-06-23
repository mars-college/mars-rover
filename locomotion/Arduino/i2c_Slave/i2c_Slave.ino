// Simple Sketch for ATTiny85
// Listens to I2C for an 8-bit value
// writes that value to PWM output

#include <TinyWire.h>

#define ADDRESS 0x11

#define PWM_PIN 1 // pin #6
#define IN1_PIN 5 // pin #1
#define IN2_PIN 3 // pin #2
#define LED_PIN 4 // pin #3

float motor_ease = 0.125;
float motor_speed = 0; // actual motor speed (0-255)
int target_speed = 0; // target motor speed (0-255)

float led_ease = 0.0125;
float brightness = 0; // LED brightness (0-255)
int target_brightness = 0; // target brightness (0-255)

boolean state = false;

//////////////////////////////////////////////////////////////////////////////

void setup() {

  //  warning: this contains cryptic register settings for the ATTiny85 timers

  cli(); // clear interrupts

  // timer0 PWM freqeuncy ~8Khz (16Mhz / 256 / 8)
  TCCR0A = 0b00000011; // waveform generation mode (WGM) = fast pwm
  TCCR0B = 0b00000010; // bits 0-2 are prescaler /8

  // timer1 frequency ~ 60Hz ( 16Mhz / 8192 / 60 ~ 32.5 )
  // used for timed smoothing PWM values
  TCCR1 = 0b10001110; //CTC - 16Mhz / 8192
  OCR1A = 0b00000000; //interrupt when the clock is reset
  OCR1C = 0b00010000; //clock is reset when it hits 32
  TIMSK = 0b01000000; // attach interrupt to OCR1A

  sei(); // set interrupts

  pinMode(PWM_PIN, OUTPUT);
  pinMode(IN1_PIN, OUTPUT);
  pinMode(IN2_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  // config TinyWire library for I2C slave functionality
  TinyWire.begin( ADDRESS );
  // sets callback for the event of a slave receive
  TinyWire.onReceive( onI2CReceive );

}

//////////////////////////////////////////////////////////////////////////////

void loop() {
  analogWrite(PWM_PIN, int(motor_speed + 0.5));
  analogWrite(LED_PIN, int(brightness+0.5));
}

//////////////////////////////////////////////////////////////////////////////

ISR(TIM1_COMPA_vect) {
  motor_speed += ease(motor_speed, target_speed, motor_ease);
  brightness += ease(brightness, target_brightness, led_ease);
}

//////////////////////////////////////////////////////////////////////////////

void onI2CReceive(int howMany) {
  byte data = 0;
  while ( TinyWire.available() > 0 ) {
    //read first byte in the buffer
    data = TinyWire.read();
    // if there are at least 1 more bytes, run the check
    if (TinyWire.available() > 0) {
      if (data == 'p') {
        target_speed = TinyWire.read();
      } else if (data == 'd') {
        setDirection( TinyWire.read() );
      } else if (data == 'l') {
        target_brightness = TinyWire.read();
      }
    }
  }
  PORTB |= 0b10;
  return;
}

//////////////////////////////////////////////////////////////////////////////

float ease(float _val, int _target, float _ease) {
  return ( float(_target) - _val ) * _ease;
}

//////////////////////////////////////////////////////////////////////////////

void setDirection(boolean dir) {
  if (dir) {
    PORTB = 1 << IN1_PIN | 0 << IN2_PIN;
  } else {
    PORTB = 0 << IN1_PIN | 1 << IN2_PIN;
  }
}
