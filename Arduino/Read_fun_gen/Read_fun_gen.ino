#include <RFduinoBLE.h>

/* ---- Design discussions -----

Why 150hz / 50hz?
    Each broadcast takes energy, so we want to minimize those as much as possible. 

    During emperical testing, 50hz was a comprimise number between unexplained deviation from the desired hz,
    (approx ~1.5hx for 50hz - So actual broadcast speed around 48.5hz), data loss (~0.4% for 50hz). 50hz, with 
    packing three data sets in each broadcast, allows for an effecive 150hz recording speed - more than what is needed.
    Lower broadcast speeds were closer to the desired hz with less loss, and likewise oppositely true for higher speeds.
    The RFduino actually didn't seem to be slowed down by transmitting more data, only by the frequency of the sending.
    Emperically derived maximum broadcast speeds were around 125hz. Data loss was relatively high at 125, averaging
    around 2-3%, peaking around 5-6% at times. 
    The reason for this, or nature of loss, was not explored further as 50hz is an adequate solution.

Why three sets of data in a broadcast?
    During testing, I was only able to broadcast 20 bytes in a single bluetooth packet. Each set takes 6 bytes, so
    this means that 3 will fit. I'm not sure whether the 20 bytes is a limitation of the RFduino, PC, or BLE 4.0
    specs, but that's what we found and stuck with it.


--- Bit shifting explained ---
Each integer takes 32 bits, which is 4 bytes. 
   00000000 00000000 00000000 00000000 

This gives us a max value of 2^32, more than we'll ever need. The Arduino's ADC (analogRead) is only
capable of creating 10 bit (2^10 = 1024) numbers. 
This means that the top 2 bytes of the int are never used, and we can safely disregard them.

So now we want to convert this int into two bytes. The way that we do this is with bit shifting and the & operator.

Getting the rightmost byte is easy - we just & the int and a byte full of ones (0xFF), e.g.,:

(example recording): 00000000 00000000 00000001 10110110
(0xFF)               00000000 00000000 00000000 11111111
(Result after &)     00000000 00000000 00000000 10110110

Save the result into a byte and you have that. Next, we want the second byte from the right. To do this, 
we shift those bits into the first byte's location, then do the same & with 0XFF.     

(example recording): 00000000 00000000 00000001 10110110
(shift right):       00000000 00000000 00000000 00000001
(0xFF)               00000000 00000000 00000000 11111111
(Result after &)     00000000 00000000 00000000 00000001

Save this in another byte and viola! You have two separate bytes. In other use cases, this could also be used
to convert 4 (or any number of) byte values (such as a float) into separate bytes.
*/



// This is the hertz at which to take measurements. We measure at this frequency, transmit at 1/3 of this.
// We transmit at 1/3 because we can fit three sets of data in each broadcast.

int recording_hertz = 150;

unsigned long t = 0;                       // Used for keeping track of time
int data;

char sendData[18];                         // This holds the data to be sent to the PC
  // 0-1  - PPG
  // 2-3  - GSR
  // 4-5  - Temperature
  // 6-15, repeat

char buffer[6];                             // This buffer is used while recording, then transfered into sendData.
  // 0-1  - PPG
  // 2-3  - GSR
  // 4-5  - Temperature


// ---- Calculated Variables ----

float period = 1/float(recording_hertz);                   // Period for recording
unsigned long micro_period = floor(period * 1000000.0);    // Period for recording in microseconds

void setup() {
  RFduinoBLE.advertisementData = "Anand";  
  
  //Serial.begin(9600);

  // start the BLE stack
  RFduinoBLE.begin();

}

void loop() {

  // Loop records three pieces of data before transmitting
  for (int i = 0; i < 3; i++) {

    while ((micros() - t) <= micro_period) {
      // Wait for our recording period to elapse. 
      // We do it this way so that, theoretically, no matter how long recording/transmitting the last data took,
      // we will loop through at the appropriate speed so that our recordings are consistent
    }
      t = micros();                   // Get start time

      // Read PPG data
      data = analogRead(2);
      buffer[0] = (data >> 8) & 0xFF;   // Bit shift top half of int down to one byte. ** See note at top
      buffer[1] = data & 0xFF;          // Copy only last byte from int

      // Read GSR data
      data = analogRead(3);
      buffer[2] = (data >> 8) & 0xFF;
      buffer[3] = data & 0xFF;

      // Read temperature data
      data = analogRead(4);
      buffer[4] = (data >> 8) & 0xFF;
      buffer[5] = data & 0xFF;        
    
    
    if ((micros() - t) < 0) {            // Micros() overflows back to 0 every ~70 minutes, this accounts for this
      t = micros();
    }

    // Save data to send data buffer
    for (int j = 0; j < 6; j++) {
      sendData[i*6+j] = buffer[j];
    }

  }

  // We've now recorded three sets of data - send to PC! 
  RFduinoBLE.send(sendData,18);

}

