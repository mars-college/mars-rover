// Simple Sketch for ATTiny85
// Generates PWM and Motor control signals from I2C messages

#include <TinyWire.h>

#define ADDRESS 0x11 // using 0x10 for left motor, 0x11 for right

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

  // Pulse Width Modulator B Enable, OCR1B cleared on compare match
  GTCCR = 0b01100000;

  // timer0 PWM freqeuncy ~8Khz (16Mhz / 256 / 8)
  TCCR0A = 0b00100011; // waveform generation mode (WGM) = fast pwm, enable OC0B clear on match
  TCCR0B = 0b00000010; // bits 0-2 are prescaler /8

  // timer1 frequency ~ 30Hz ( 16Mhz / 1024 / 256 ~ 61 Hz )
  // used for timed smoothing PWM values

  TCCR1 = 0b01001010; //PWM - 16Mhz / 2048
  OCR1C = 0b11111111; //clock is reset when it hits TOP
  TIMSK = 0b01000000; // attach interrupt to TOV1 when timer1 counter exceeds OCR1C

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
}

//////////////////////////////////////////////////////////////////////////////

ISR(TIM1_COMPA_vect) {
  motor_speed += ease(motor_speed, target_speed, motor_ease);
  brightness += ease(brightness, target_brightness, led_ease);
  OCR0B = int(motor_speed + 0.1);
  OCR1B = int(brightness + 0.1);
}

//////////////////////////////////////////////////////////////////////////////

void onI2CReceive() {
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
      } else if (data == 'b') {
        target_brightness = TinyWire.read();
      }
    }
  }
  PORTB |= 0b101;
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
