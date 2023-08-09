# import RPi.GPIO as GPIO
import asyncio
import time
import pigpio

# GPIO.setmode(GPIO.BCM)

SERVO_PIN = 12
PWM_FREQ = 50

minDutyCycle=48

pwm = pigpio.pi()
pwm.set_mode(SERVO_PIN, pigpio.OUTPUT)

async def setServo(d):
    pwm.set_PWM_frequency( SERVO_PIN, 50)
    print("[Card] Setting duty cycle of " + str(d))
    pwm.set_servo_pulsewidth( SERVO_PIN, d)
    
async def powerOff():
    print("[Card] Shutting off servo. (freq zero) ")
    pwm.set_PWM_frequency( SERVO_PIN, 0)