from gpiozero import Button
from signal import pause
from datetime import datetime
import threading
import time

gpio_handler_map = {}

def press_handler_selector(arg):
    global gpio_handler_map
    gpio_handler_map[arg.pin.number]()

class GpioHandler:
    def __init__(self, gpio_line, handler):
        global gpio_handler_map
        self._btn = Button(gpio_line, pull_up=False)
        self._btn.when_pressed = press_handler_selector
        gpio_handler_map[gpio_line] = self.__handle_press
        self._counting = False
        self._counter = 0
        self._thread = None
        self._handler = handler
    def __thread_handler(self):
        time.sleep(0.1)
        self._handler(self._counter)
        self._counting = False
        _counter = 0
        _thread = None
    def __handle_press(self):
        print("Press")
        if self._counting:
            self._counter += 1
        else:
            self._counting = True
            self._counter = 1
            self._thread = threading.Thread(target=self.__thread_handler)
            self._thread.start()

# test
def sample_handler(evt):
    print("Event: {}".format(evt))

gpio_handler = GpioHandler(22, sample_handler)

pause()
