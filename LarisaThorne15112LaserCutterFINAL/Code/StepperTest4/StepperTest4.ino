// 15-112 TERM PROJECT: LASER CUTTER
// LARISA THORNE (lthorne), Section A
// Current version: 2015 - 12 - 08
// Stepper motor serial command test, Arduino side

#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

// Create the motor shield object:
// Bottom shield:
Adafruit_MotorShield AFMSbottom(0x60);
// Top shield: 
Adafruit_MotorShield AFMStop(0x61);  

// Let motor port #1 be (M1, M2) and #2 be (M3, M4)
Adafruit_StepperMotor *xStepper = AFMSbottom.getStepper(200, 2);
Adafruit_StepperMotor *yStepper = AFMStop.getStepper(200,2);

int xPos = 0;
int yPos = 0;
int laserOn = 0;
int input = 0;
int isY = 0; // laser state = 0, x = 1, y = 2
int motorSpeed = 10;
int laserPin = 13;


void setup() {
  pinMode(laserPin, OUTPUT);
  Serial.begin(9600);  // set up Serial library at 9600 bps
  //Serial.println("Stepper test!");
  AFMSbottom.begin();  // create with the default frequency 1.6KHz
  AFMStop.begin();
  xStepper->setSpeed(motorSpeed);  // in rpm
  yStepper->setSpeed(motorSpeed);
}

void loop() {
  if (Serial.available() > 0){
    input = Serial.parseInt(); // Get list element
    
    // Found laser state:
    if (isY == 0) {
      laserOn = input;
      if (laserOn == 0) {
        digitalWrite(laserPin, LOW);
      }
      else {
        digitalWrite(laserPin, HIGH);
      }
    }
    
    // Found x-component:
    
    else if (isY == 2) { 
      xPos = input;
      if (xPos > 0) {
        motorSpeed = 10;
        xStepper->setSpeed(motorSpeed);
        xStepper->step(xPos, BACKWARD, SINGLE);
      }
      if (xPos < 0) {
        xPos = abs(xPos);
        motorSpeed = 10;
        xStepper->setSpeed(motorSpeed);
        xStepper->step(xPos, FORWARD, SINGLE);
      }
      if (xPos == 0) {
        motorSpeed = 0;
        xStepper->setSpeed(motorSpeed);
      }
    }
    
    // Found y-component:
    
    else if (isY == 1) {
      yPos = input;
      if (yPos > 0) {
        motorSpeed = 10;
        yStepper->setSpeed(motorSpeed);
        yStepper->step(yPos, BACKWARD, SINGLE);
      }
      if (yPos < 0) {
        yPos = abs(yPos);
        motorSpeed = 10;
        yStepper->setSpeed(motorSpeed);
        yStepper->step(yPos, FORWARD, SINGLE);
      }
      if (yPos == 0) {
        motorSpeed = 0;
        yStepper->setSpeed(motorSpeed);
      }
    }

      
    // Now increment isY tag:
    
    if (isY == 0) {
      isY = 1;
    }
    else if (isY == 1) {
      isY = 2;
    }
    else { // isY == 2
      isY = 0;
    }
  }

  // To deal with end-of-list behavior:
  
  else {
    motorSpeed = 0;
    xStepper->setSpeed(motorSpeed);
    yStepper->setSpeed(motorSpeed);

  }
 
  
}

