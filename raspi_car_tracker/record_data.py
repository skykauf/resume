# import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from datetime import datetime
import gps
import os
from config import *
import requests

class DataRecorder:
    def __init__(self,max_dur=10):
        self.isStarted = False
        self.printAll=True
        self.max_duration = max_dur
        
        self.start_datetime = datetime.now()
        self.script_start_datedir = os.path.join(datadir,self.start_datetime.strftime("%m-%d-%Y"))
        self.script_start_datetime = self.start_datetime.strftime("%m-%d-%Y_%H:%M:%S")
        self.start_timestamp = datetime.timestamp(self.start_datetime)

        self.gps_filepath = os.path.join(self.script_start_datedir,"GPS_"+self.script_start_datetime+'.csv')

    def initialize_gps(self):
        # Listen on port 2947 (gpsd) of localhost
        session = gps.gps("localhost", "2947")
        session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.lats=[]
        self.longs=[]
        self.latlongs=[]
        print("Starting record")
        with open(self.gps_filepath,'w') as f:
            f.write('latitude,longitude,gps_timestamp\n')
            while True:
                try:
                    report = session.next()
                    if self.printAll:
                        print(report)
                    # Wait for a 'TPV' report and display the current time
                    local_timestamp = datetime.timestamp(datetime.now())
                    if report['class'] == 'TPV':
                        lat = report['lat']
                        lon = report['lon']
                        self.lats.append(lat)
                        self.longs.append(lon)
                        self.latlongs.append(str(lat))
                        self.latlongs.append(str(lon))
                        # store data in csv file
                        f.write(str(lat)+','+str(lon)+','+str(local_timestamp)+'\n')
                        
                    if local_timestamp-self.start_timestamp >self.max_duration:
                        print(self.max_duration,"seconds elapsed")
                        break
                except KeyError:
                    print("GPS not returning latitude or longitude")
                    break
                except StopIteration:
                    session = None
                    print("GPSD has terminated")
                    
    def write_gps_route_raw(self):
        map_params = {"key":openstreetmap_apikey,"bestfit":",".join([str(min(self.lats)-.01), str(min(self.longs)-.01), str(max(self.lats)+.01), str(max(self.longs)+.01)]), "size":"1920, 960", "shape":",".join(self.latlongs)}

        mapimage = requests.get("http://www.mapquestapi.com/staticmap/v4/getmap", params=map_params)
        if mapimage.status_code == 200:
            print("Successfully retrieved image")
        else:
            print("Couldn't retrieve image")
            print(mapimage.text)
        i = Image.open(BytesIO(mapimage.content))
        i.save(os.path.join(self.script_start_datedir,"ROUTEMAP_"+self.script_start_datetime+".jpg"))
        print("saved image to", self.script_start_datedir)
        print("SHOWN")

    def button_callback(channel):
        print("Button was pushed, flipping states!")
        if self.isStarted:
            self.isStarted = False
        else:
            self.isStarted = True

# add a callback to external on/off button
# GPIO.setwarnings(False) # Ignore warning for now
# GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
# GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
# GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge

