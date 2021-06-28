import gps
from datetime import datetime
import requests
from config import *
import shutil
from PIL import Image
from io import BytesIO
import os

max_duration = 10

start_datetime = datetime.now()
script_start_datedir = os.path.join(datadir,start_datetime.strftime("%m-%d-%Y"))
script_start_datetime = start_datetime.strftime("%m-%d-%Y_%H:%M:%S")
start_time = datetime.timestamp(start_datetime)

os.makedirs(script_start_datedir,exist_ok=True)
print(script_start_datedir)
# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
lats=[]
longs=[]
latlongs=[]
print("Starting record")
with open(os.path.join(script_start_datedir,"GPS_"+script_start_datetime+'.csv'),'w') as f:
    f.write('latitude,longitude,gps_timestamp\n')
    while True:
        try:
            report = session.next()
            # Wait for a 'TPV' report and display the current time
            if report['class'] == 'TPV':
                lat = report['lat']
                lon = report['lon']
                local_timestamp = datetime.timestamp(datetime.now())
                lats.append(lat)
                longs.append(lon)
                latlongs.append(str(lat))
                latlongs.append(str(lon))
                # store data in csv file
                f.write(str(lat)+','+str(lon)+','+str(local_timestamp)+'\n')
                
                if local_timestamp-start_time >max_duration:
                    print(max_duration,"seconds elapsed")
                    break
        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except Exception as E:
            print(E)
        except StopIteration:
            session = None
            print("GPSD has terminated")

script_end_datetime = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
print(len(lats))
print(len(longs))

map_params = {"key":openstreetmap_apikey,"bestfit":",".join([str(min(lats)-.01), str(min(longs)-.01), str(max(lats)+.01), str(max(longs)+.01)]), "size":"1920, 960", "shape":",".join(latlongs)}


mapimage = requests.get("http://www.mapquestapi.com/staticmap/v4/getmap", params=map_params)
if mapimage.status_code == 200:
    print("Successfully retrieved image")
else:
    print("Couldn't retrieve image")
    print(mapimage.text)

i = Image.open(BytesIO(mapimage.content))
i.save(os.path.join(script_start_datedir,"ROUTEMAP_"+script_start_datetime+"_to_"+script_end_datetime+".jpg"))
print("saved image to", script_start_datedir)
print("SHOWN")
