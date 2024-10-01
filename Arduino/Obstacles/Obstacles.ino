#include <AFMotor.h>

#define Trigger_pin A0 //left
#define Echo_pin A1// left
#define Trigger_pin1 A2 // mid
#define Echo_pin1 A3 // mid
#define Trigger_pin2 A4 // right
#define Echo_pin2 A5 //right
#define sensor_R 10
#define sensor_L 9

int value1;
String value2;
unsigned int count=0;
byte SPEED = 180;
int dis_ultrasonic_1 = 0;
int dis_ultrasonic_2 = 0;
int dis_ultrasonic = 0;

AF_DCMotor motor1(1, MOTOR12_1KHZ);
AF_DCMotor motor2(2, MOTOR12_1KHZ);
AF_DCMotor motor3(3, MOTOR34_1KHZ);
AF_DCMotor motor4(4, MOTOR34_1KHZ);

void setup(){
  Serial.begin(115200);

  //setup ultrasound sensor
  pinMode(Trigger_pin, OUTPUT);
  pinMode(Echo_pin, INPUT);
  pinMode(Trigger_pin1, OUTPUT);
  pinMode(Echo_pin1, INPUT);
  pinMode(Trigger_pin2, OUTPUT);
  pinMode(Echo_pin2, INPUT);

  //setup ir sensor
  pinMode(sensor_R, INPUT); //declare ir sensor as input
  pinMode(sensor_L, INPUT); //declare ir sensor as input
  
}

void loop(){
 obstacles();
}

void line_check(){
  if(digitalRead(sensor_L) == 1 && digitalRead(sensor_R) == 1){
  forward();
 }
  else if(digitalRead(sensor_L) == 0 && digitalRead(sensor_R) == 1){
    right();
 }
  else if(digitalRead(sensor_L) == 1 && digitalRead(sensor_R) == 0){
    left();
 }
  else Stop();
  delay(100);
}

void receive_info(){
  if (Serial.available() > 0){
    String receiveString = Serial.readString();
    if (receiveString.startsWith("Distance:")){
      value1 = receiveString.substring(9).toInt();
    }
    else if (receiveString.startsWith("Sign:")){
      value2 = receiveString.substring(5);
    }
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

void obstacles(){
  dis_ultrasonic = Distance(1);
  receive_info();
  delay(100);
  // Serial.println(value1);

  if(value1 > 30  && count == 0){
    line_check();
    delay(10);
  }
  else if (value1 <= 30  && (count >=0 && count < 2)){
    delay(50);
    dis_ultrasonic_1 = Distance(0);
    delay(100);
    if (dis_ultrasonic_1 >= 20){
      turn_left();
      delay(100);
      Stop();
      delay(100);
    }
    else {
      Stop();
    }
  }
  else if (value1 > 30  && (count >= 1 && count <= 2)){
    delay(50);
    dis_ultrasonic_2 = Distance(2);
    delay(200);
    if(dis_ultrasonic_2 >= 20){
      turn_right();
      delay(10);
      Stop(); 
    }
    else {
      Stop();
    }
  }
  else {
    Stop();
  }
}

void turn_left(){
  count += 1;
  execute_turn(left_1, sensor_L, right_1);
}

void turn_right(){
  count -= 1;
  execute_turn(right_1, sensor_R, left_1);
}

void execute_turn(void (*firstTurn)(), int sensorPin, void (*secondTurn)()){
  firstTurn();
  delay(700);
  forward();
  while(digitalRead(sensorPin) == 0){};
  delay(800);
   
  secondTurn();
  delay(600);
  Stop();
  delay(100);
  dis_ultrasonic_2 = Distance(2);

  while(dis_ultrasonic_2 < 20){
    dis_ultrasonic = Distance(1);
    delay(10);
    dis_ultrasonic_2 = Distance(2);
    delay(10);
    if(dis_ultrasonic > 30){
      line_check();
      delay(300);
    }
    else {
      Stop();
      delay(300);
      break;
    }
  }
}

void forward(){
  motor1.setSpeed(SPEED);
  motor2.setSpeed(SPEED);
  motor3.setSpeed(SPEED);
  motor4.setSpeed(SPEED);

  motor1.run(FORWARD);
  motor2.run(FORWARD);  //rotate the motor clockwise
  motor3.run(FORWARD);  
  motor4.run(FORWARD);  
}

void left(){
  motor1.setSpeed(SPEED);
  motor2.setSpeed(SPEED);
  motor3.setSpeed(SPEED);
  motor4.setSpeed(SPEED);
  
  motor1.run(BACKWARD); //rotate the motor anti-clockwise
  motor2.run(BACKWARD); 
  motor3.run(FORWARD);  //rotate the motor clockwise
  motor4.run(FORWARD);  
}

void left_1(){
  motor1.setSpeed(255);
  motor2.setSpeed(255);
  motor3.setSpeed(255);
  motor4.setSpeed(255);
  
  motor1.run(BACKWARD); //rotate the motor anti-clockwise
  motor2.run(BACKWARD); 
  motor3.run(FORWARD);  //rotate the motor clockwise
  motor4.run(FORWARD);  
}

void right(){
  motor1.setSpeed(SPEED);
  motor2.setSpeed(SPEED);
  motor3.setSpeed(SPEED);
  motor4.setSpeed(SPEED);
  
  motor1.run(FORWARD);  //rotate the motor clockwise
  motor2.run(FORWARD);  
  motor3.run(BACKWARD); //rotate the motor anti-clockwise
  motor4.run(BACKWARD); 
}

void right_1(){
  motor1.setSpeed(255);
  motor2.setSpeed(255);
  motor3.setSpeed(255);
  motor4.setSpeed(255);
  
  motor1.run(FORWARD);  //rotate the motor clockwise
  motor2.run(FORWARD);  
  motor3.run(BACKWARD); //rotate the motor anti-clockwise
  motor4.run(BACKWARD); 
}

void Stop(){
  motor1.run(RELEASE); //stop the motor when release the button
  motor2.run(RELEASE); 
  motor3.run(RELEASE); 
  motor4.run(RELEASE);
}