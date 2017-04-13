#include <RFduinoBLE.h>

int recording_hertz = 50;

unsigned long t1 = 0;                       // Used for keeping track of time
unsigned long t2 = 0;
unsigned long t3 = 0;

int datastream1 = 0;

int count = 0;


void setup() {
  RFduinoBLE.advertisementData = "Anand";  
  
  RFduinoBLE.begin();  

  Serial.begin(9600);
}

void loop() {
  t1 = micros();
  datastream1 = analogRead(2); 
  t2 = micros(); 
  RFduinoBLE.sendInt(datastream1);  
  t3 = micros();

  Serial.print(count);
  Serial.print(",");
  Serial.print(t2-t1);
  Serial.print(",");
  Serial.println(t3-t2);

  count += 1;
  delay(50);

 


}
