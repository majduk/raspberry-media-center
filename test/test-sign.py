from gpiozero import LED
from time import sleep

led = LED(24)

while True:
    led.on()
    led.off()
    led.on()
    led.off()
    led.on()
    led.off()
    led.on()
    led.off()
    sleep(1)
