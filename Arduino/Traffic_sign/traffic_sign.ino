// import library
#include <AFMotor.h>

//define variable
#define Trigger_pin A0 //left
#define Echo_pin A1// left
#define Trigger_pin1 A2 // mid
#define Echo_pin1 A3 // mid
#define Trigger_pin2 A4 // right
#define Echo_pin2 A5 //right
#define sensor_R 10
#define sensor_L 9

//initial motor pin
AF_DCMotor motor1(1, MOTOR12_1KHZ);
AF_DCMotor motor2(2, MOTOR12_1KHZ);
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);

void setup(){
  Serial.begin(115200);

  //setup ir sensor
  pinMode(sensor_R, INPUT); // declare ir sensor as input
  pinMode(sensor_L, INPUT); // declare ir sensor as input
  
}

void loop(){
  sign_check();
}

void line_check(){
  if (digitalRead(sensor_L) == 1 && digitalRead(sensor_R) == 1){
    forward();
  }
  else if (digitalRead(sensor_L) == 0 && digitalRead(sensor_R) == 1){
    right();
  }
  else if (digitalRead(sensor_L) == 1 && digitalRead(sensor_R) == 0){
    left();
  }
  delay(10);
}

void sign_check(){
  char sign_detect = receive_inf();
  delay(10);
  if(sign_detect == 'g'){ 
    forward();
  }
  else if(sign_detect == 'y'){
    go_slow();
  }
  else if(sign_detect == 'l'){ 
    left();
    delay(100);
    line_check();
  }
  else if(sign_detect == 'r' || sign_detect == 's'){ 
    go_slow();
    delay(1000);
    Stop();
  }
  else line_check();
  delay(100);      
}

void sign_check_special(){
  char sign_detect = receive_inf();
  int dis_ultrasonic = Distance(1);
  if (dis_ultrasonic < 40){
    if(sign_detect == 'o'){
      Stop();
      delay(50);
    }
    else if(sign_detect != 'o'){
      Stop();
      delay(50);
      left();
      delay(700);
      forward();
      delay(1000);
      right();
      delay(700);
      Stop();
      delay(10);
      line_check();
      delay(30);
    }
  }
  else line_check();
  delay(30);
}

char receive_inf(){
  if(Serial.available() > 0){
    char reads = Serial.read();
    Serial.print("Received: ");
    Serial.println(reads);
    return reads;
  }
}

unsigned long getMeasure(int triggerPin, int echoPin){
  digitalWrite(Trigger_pin,LOW);
  delayMicroseconds(2);
  digitalWrite(Trigger_pin,HIGH);
  delayMicroseconds(5);
  digitalWrite(Trigger_pin,LOW);

  return pulseIn(echoPin, HIGH, 20000);
}

unsigned int Distance(byte option){
  unsigned long measure = 0;
  unsigned int distance = 0;

  switch(option){
    case 0:
      measure = getMeasure(Trigger_pin, Echo_pin);
      break;
    case 1:
      measure = getMeasure(Trigger_pin1, Echo_pin1);
      break;
    case 2:
      measure = getMeasure(Trigger_pin2, Echo_pin2);
      break;
    default:
      return 250;
  }

  distance = (measure/2/29.412);
  if (distance == 0) {
    distance = 250;  // Set a default maximum value if no measurement
  }
  return distance;
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

void go_slow(){
  motor1.setSpeed(160);
  motor2.setSpeed(160);
  motor3.setSpeed(160);
  motor4.setSpeed(160);

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