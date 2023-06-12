import RPi.GPIO as GPIO
import asyncio
import time

GPIO.setmode(GPIO.BCM)

SERVO_PIN = 12
PWM_FREQ = 50

minDutyCycle=48

GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, PWM_FREQ)
pwm.start(0)

async def setServo(d):
    print("[Card] Pulsing duty cycle of " + str(d))
    pwm.ChangeDutyCycle(d)
    time.sleep(0.2)
    pwm.ChangeDutyCycle(0)