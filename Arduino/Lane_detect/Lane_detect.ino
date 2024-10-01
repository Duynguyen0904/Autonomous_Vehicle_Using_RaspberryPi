// import library
#include <AFMotor.h>

//initial motor pin
AF_DCMotor motor1(1, MOTOR12_1KHZ);
AF_DCMotor motor2(2, MOTOR12_1KHZ);
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);

void setup(){
  Serial.begin(115200);
}

void loop(){
  lane_check();
}

void lane_check(){
  char lane_data = receive_inf();
  delay(10);
  if(lane_data == 'f'){ 
    forward();
  }
  else if(lane_data == 'l'){ 
    left();
  }
  else if(lane_data == 'r'){ 
    right();
  }
  else Stop();
  delay(100);      
    }

char receive_inf(){
  if(Serial.available() > 0){
    char reads = Serial.read();
    Serial.print("Received: ");
    Serial.println(reads);
    return reads;
  }
}

void forward(){
  motor1.setSpeed(180);
  motor2.setSpeed(180);
  motor3.setSpeed(180);
  motor4.setSpeed(180);

  motor1.run(FORWARD);  //rotate the motor clockwise
  motor2.run(FORWARD);  //rotate the motor clockwise
  motor3.run(FORWARD);  //rotate the motor clockwise
  motor4.run(FORWARD);  //rotate the motor clockwise
}

void left(){
  motor1.setSpeed(255);
  motor2.setSpeed(255);
  motor3.setSpeed(255);
  motor4.setSpeed(255);

  motor1.run(BACKWARD); //rotate the motor anti-clockwise
  motor2.run(BACKWARD); //rotate the motor anti-clockwise
  motor3.run(FORWARD);  //rotate the motor clockwise
  motor4.run(FORWARD);  //rotate the motor clockwise
  
}

void right(){
  motor1.setSpeed(255);
  motor2.setSpeed(255);
  motor3.setSpeed(255);
  motor4.setSpeed(255);
  
  motor1.run(FORWARD);  //rotate the motor clockwise
  motor2.run(FORWARD);  //rotate the motor clockwise
  motor3.run(BACKWARD); //rotate the motor anti-clockwise
  motor4.run(BACKWARD); //rotate the motor anti-clockwise
}
void Stop(){
  motor1.run(RELEASE); //stop the motor when release the button
  motor2.run(RELEASE); //rotate the motor clockwise
  motor3.run(RELEASE); //stop the motor when release the button
  motor4.run(RELEASE); //stop the motor when release the button
}