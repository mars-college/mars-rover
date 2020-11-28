// Simple Sketch for ATTiny85
// Generates PWM and Motor control signals from I2C messages
// TB67H420FTG Dual/Single Motor Driver Carrier - https://www.pololu.com/product/2999

#include <TinyWire.h>

#define ADDRESS 0x10 // using 0x10 for left motor, 0x11 for right
//#define ADDRESS 0x11 // using 0x10 for left motor, 0x11 for right

#define PWM_PIN 1 // PB1 - 1 = DIP8 pin #6
#define IN1_PIN 3 // PB1 - 3 = DIP8 pin #2
#define IN2_PIN 4 // PB1 - 4 = DIP8 pin #3

float motor_ease = 0.25;
float motor_speed = 0; // actual motor speed (0-255)
uint8_t target_speed = 0; // target motor speed (0-255)
byte dir = 0;
//////////////////////////////////////////////////////////////////////////////

void setup() {

  //  WARNING: the followingcode  contains cryptic register settings for the ATTiny85 timers.
  //  Please refer to the ATTiny85 Datasheet/Manual for details.

  cli(); // clear interrupts

  // Pulse Width Modulator B Enable, OCR1B cleared on compare match
//  GTCCR = 0b01100000; // PB4 enabled
  GTCCR = 0b01000000; // PB4 disabled

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

  // config TinyWire library for I2C slave functionality
  TinyWire.begin( ADDRESS );
  // sets callback for the event of a slave receive & request
  TinyWire.onReceive( onI2CReceive );
  TinyWire.onRequest( onI2CRequest );
}

//////////////////////////////////////////////////////////////////////////////

void loop() {
}

//////////////////////////////////////////////////////////////////////////////

ISR(TIM1_COMPA_vect) {
  motor_speed += ease(motor_speed, target_speed, motor_ease);
  OCR0B = int(motor_speed);
}

//////////////////////////////////////////////////////////////////////////////
int onI2CReceive() {
  byte data = 0;

  // loop through all the data
  while ( TinyWire.available() > 0 ) {
    
    //read first byte in the buffer
    data = TinyWire.read();
    
    // if there are at least 1 more bytes, run the check
    if (TinyWire.available() > 0) {
      
      if (data == 'p') {
        target_speed = TinyWire.read();
        TinyWire.write(String("Got: ").concat(String(target_speed)));
      } else if (data == 'd') {
        dir = TinyWire.read();
        setDirection( dir );
        TinyWire.write(String("Got: ").concat(String(dir)));
      } else {
        // bad data
        TinyWire.write("Got bad data.");
        return 1;
      }
      
    } else {
      // expecting more bytes
      TinyWire.write("Got too few bytes.");
      return 1;
    }
  }
  
  PORTB |= 0b101;
  return 0;
}

//////////////////////////////////////////////////////////////////////////////

void onI2CRequest() {
  // sends one byte with content 'b' to the master, regardless how many bytes he expects
  // if the buffer is empty, but the master is still requesting, the slave aborts the communication
  // (so it is not blocking)
  TinyWire.send('b');
}

//////////////////////////////////////////////////////////////////////////////

float ease(float _val, int _target, float _ease) {
  return ( float(_target) - _val ) * _ease;
}

//////////////////////////////////////////////////////////////////////////////
// Super 1337 way of setting pin states way faster than digitalWrite()

void setDirection(boolean dir) {
  if (dir) {
    PORTB = ( PORTB & 0b100111 ) | ( ( (1 << IN1_PIN) & 0b001000 ) | ( (0 << IN2_PIN ) & 0b010000 ) );
  } else {
    PORTB = ( PORTB & 0b100111 ) | ( ( (0 << IN1_PIN) & 0b001000 ) | ( (1 << IN2_PIN ) & 0b010000 ) );
  }
}
