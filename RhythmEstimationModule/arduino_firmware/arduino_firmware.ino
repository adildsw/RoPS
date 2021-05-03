#include "ICM_20948.h"

ICM_20948_I2C myICM;

unsigned long peak_time[] = {0, 0, 0};
unsigned long last_move_time = 0;
int count = 0;

int UPPER_THRESH = 1800;
int LOWER_THRESH = 0;
int INTER_MOVE_TIME_THRESH = 1500;

bool counter_flag = true;

float ay = 0;
float bpm = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  Wire.setClock(400000);

  myICM.begin(Wire, 1);
}

void loop() {
  if (myICM.dataReady()) {
    myICM.getAGMT();
    ay = myICM.accY();

//    Serial.println(ay);

    

    if (ay >= UPPER_THRESH && counter_flag) {
      if (millis() - last_move_time >= INTER_MOVE_TIME_THRESH) {
//      Serial.println("Reset");
      count = 0;
    }
      peak_time[count] = millis();
      last_move_time = millis();
      count++;
      counter_flag = false;
//      Serial.println("Recorded");
    }
    else if (ay <= LOWER_THRESH) {
      counter_flag = true;
    }

    if (count == 3) {
      count = 0;
      bpm = ((60000/(peak_time[1] - peak_time[0])) + (60000/(peak_time[2] - peak_time[1])))/2;
      Serial.println(bpm);
    }
  }
}
