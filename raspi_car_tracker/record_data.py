# import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from datetime import datetime
import gps
import os
from config import *
import requests
from PIL import Image
from io import BytesIO
import cv2

# experimental
# import multiprocessing

class DataRecorder:
    def __init__(self,max_dur=10000):
        self.isStarted = False
        self.printAll=False # debugging variable
        self.max_duration = max_dur # maximum number of seconds to collect data
        
        # time metadata and save folder
        self.start_datetime = datetime.now()
        self.script_start_datetime = self.start_datetime.strftime("%m-%d-%Y_%H:%M:%S")
        self.start_timestamp = datetime.timestamp(self.start_datetime)

        # save folder and filenames
        self.script_start_datedir = os.path.join(datadir,self.start_datetime.strftime("%m-%d-%Y"))
        self.gps_filepath = os.path.join(self.script_start_datedir,"GPS_"+self.script_start_datetime+'.csv')
        self.video_filepath = os.path.join(self.script_start_datedir,"camera_"+self.script_start_datetime+'.mp4')
        
        # sensor params
        self.fps = 20
        self.camera_resolution = (640, 480) # change when better camera


    def initialize_gps(self):
        # Listen on port 2947 (gpsd) of localhost
        self.gps_session = gps.gps("localhost", "2947")
        self.gps_session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.gps_writer = open(self.gps_filepath,'w')

        self.lats=[]
        self.longs=[]
        self.latlongs=[]
        print("Started GPS")

    def record_gps(self):
        self.gps_writer.write('latitude,longitude,gps_timestamp\n')
        try:
            report = self.gps_session.next()
            if self.printAll:
                print(report)
            # Wait for a 'TPV' report and display the current time
            local_timestamp = datetime.timestamp(datetime.now())
            if report['class'] == 'TPV' and report['mode'] > 1:
                lat = report['lat']
                lon = report['lon']
                self.lats.append(lat)
                self.longs.append(lon)
                self.latlongs.append(str(lat))
                self.latlongs.append(str(lon))
                # store data in csv file
                self.gps_writer.write(str(lat)+','+str(lon)+','+str(local_timestamp)+'\n')
            else:
                print("GPS not returning latitude or longitude")

            if local_timestamp-self.start_timestamp >self.max_duration:
                print(self.max_duration,"seconds elapsed")
                break
        except KeyError:
            break
        except StopIteration:
            # self.gps_session = None
            print("GPSD has terminated")

    def initialize_camera(self):
        self.camera_writer = cv2.VideoWriter(self.video_filepath, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, self.camera_resolution, True)
        self.camera_stream = cv2.VideoCapture(0)
        
    def record_camera(self):
        ret, frame = self.camera_stream.read()
        if ret:
            self.camera_writer.write(frame)
            cv2.imshow('Video', frame) # debugging, remove later
        else:
            print("No camera found")
            # ret, frame = self.camera_stream.read()
            # if cv2.waitKey(1) & 0xFF==ord("q"):
            #     break
            # if not self.isStarted:
            #     break

    def shutdown_gps(self):
        self.gps_session = None
        self.gps_writer.close()
        print("GPS has terminated")

    def shutdown_camera(self):
        self.camera_stream.release()
        self.camera_writer.release()
        cv2.destroyAllWindows() # remove later
        print("Camera has terminated")
                    
    def write_gps_route_to_image(self): # TODO move to different class, call upon gps shutdown?
        # may want to reduce number of coordinates sent in map-query
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

recorder = DataRecorder(100)

recorder.initialize_gps()
recorder.initialize_camera()

recorder.shutdown_gps()
recorder.shutdown_camera()