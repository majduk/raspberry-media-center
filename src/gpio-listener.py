#!/usr/bin/python3 -u
from gpiozero import Button
from signal import pause
from datetime import datetime
from subprocess import check_call
import threading
import time
import traceback

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
        try:
            self._handler(self._counter)
        except:
            traceback.print_exc()
        self._counting = False
        _counter = 0
        _thread = None
    def __handle_press(self):
        if self._counting:
            self._counter += 1
        else:
            self._counting = True
            self._counter = 1
            self._thread = threading.Thread(target=self.__thread_handler)
            self._thread.start()

def mpd_channel_handler(evt):
    print("GPIO Event: {}".format(evt))
    if evt == 5:
        try:
            check_call(['mpc','next'])
            check_call(['mpc','play'])
        except:
            check_call(['mpc','load', 'radio.mpl'])
            check_call(['mpc','play'])



if __name__ == '__main__':
    gpio_handler = GpioHandler(22, mpd_channel_handler)
    pause()
