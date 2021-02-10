import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import datetime

class DataRecorder:
    def __init__(self):
        self.isStarted = False
        self.start_datetime = datetime.now()
        self.script_start_date = start_datetime.strftime("%m-%d-%Y"))
        self.script_start_datetime = start_datetime.strftime("%m-%d-%Y_%H:%M:%S")
        self.start_timestamp = datetime.timestamp(start_datetime)



    def button_callback(channel):
        print("Button was pushed, flipping states!")
        if self.isStarted:
            self.isStarted = False
        else:
            self.isStarted = True

# add a callback to external on/off button
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge

