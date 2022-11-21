import requests
import time
import json
import numpy as np
import blockchain
import BusClass
import queue
import schedule as sc

q = queue.Queue()
url = "https://api.thingspeak.com/channels/1704499/feeds.json?api_key=Z70IVJ1X27AVPQ6C&results=2"
Rkey = "MC9FFB16PZV2BSWR"
latStation = [7.865661,7.881308,7.893300,7.887864,7.890755,7.882510,7.885414] # lat of stantion point
lonStation = [98.397750,98.364982,98.368747,98.371470,98.390563,98.404646,98.430988] # lon of stantion point
bc = blockchain.Blockchain()# create first blockchain
distanceFormGoal = 0
speed = 0
enitalB1 = 0
enitalB2 = 0
estimateTimeToBusStop = 0

def getBusStopPoint( stID ) :

    stationId = stID
    point = []

    if stationId == "1.0" :
        point = [latStation[0],lonStation[0]]
    
    elif stationId == "2.0" :
        point = [latStation[1],lonStation[1]]
    
    elif stationId == "3.0" :
        point = [latStation[2],lonStation[2]]
    
    elif stationId == "4.0" :
        point = [latStation[3],lonStation[3]]
    
    elif stationId == "5.0" :
        point = [latStation[4],lonStation[4]]
    
    elif stationId == "6.0" :
        point = [latStation[5],lonStation[5]]
    
    elif stationId == "7.0" :
        point = [latStation[6],lonStation[6]]
        
    else:
        point = ["X","X"]
        
    return point



def addData(data):
    
    baseUrlWr = "https://api.thingspeak.com/update?api_key="
    urlWr = baseUrlWr + Rkey
    dataAdd = ""
    for i in range(len(data)):
        dataAdd = dataAdd + "&field"+ str(i+1) +"=" + str(data[i])
        
    urlWr = baseUrlWr + Rkey + dataAdd

    requests.get(urlWr)
    print("!!! Data Already Add to ThingSpeak Server")
    
    
    
def readURL():
    resp = requests.get(url)
    data_disc = json.loads(resp.text)
    if((data_disc["feeds"][0]["field1"] != data_disc["feeds"][1]["field1"])|
       (data_disc["feeds"][0]["field2"] != data_disc["feeds"][1]["field2"])|
       (data_disc["feeds"][0]["field3"] != data_disc["feeds"][1]["field3"])|
       (data_disc["feeds"][0]["field4"] != data_disc["feeds"][1]["field4"])|
       (data_disc["feeds"][0]["field5"] != data_disc["feeds"][1]["field5"])   
      ):
        resp = requests.get(url)
        data_disc = json.loads(resp.text)
        q.put(data_disc)
        print("Total queue:" + str(q.qsize()))
        data_disc_pre = data_disc
    else:
        print("!Data are same dont add queu to the blockchain")
        
        
        
sc.every(25).seconds.do(readURL)

while (bc.is_chain_valid()):   
    
    sc.run_pending()
    
    if(q.qsize() >= 1):
               
        data_disc = q.get()
        busID = data_disc["feeds"][1]["field5"]
        stationID = data_disc["feeds"][1]["field4"]
        busStopPoint = getBusStopPoint(stationID)

        if(busStopPoint == ["X","X"]):
            print("Station ID is invalid (1 - 7)")
            break

        if(not ((busID == '1.0')|(busID == '2.0'))):
            print("Bus ID is invalid (1 - 2)")
            break

        if((busID == '1.0') & (enitalB1 == 0)):

            busId1 = BusClass.Bus(float(data_disc["feeds"][1]["field1"]),float(data_disc["feeds"][1]["field2"])) 
            distanceFormGoal = busId1.distanceFormGoal(busStopPoint[0],busStopPoint[1])
            speed = busId1.readSpeed()
            enitalB1 = 1;

        if((busID == '2.0') & (enitalB2 == 0)):

            busId2 = BusClass.Bus(float(data_disc["feeds"][1]["field1"]),float(data_disc["feeds"][1]["field2"])) 
            distanceFormGoal = busId2.distanceFormGoal(busStopPoint[0],busStopPoint[1])
            speed = busId2.readSpeed()
            enitalB2 = 1;

        if((busID == '1.0') & (enitalB1 > 1)):

            busId1.setBusLocation(float(data_disc["feeds"][1]["field1"]),float(data_disc["feeds"][1]["field2"]))
            distanceFormGoal = busId1.distanceFormGoal(busStopPoint[0],busStopPoint[1])
            speed = busId1.readSpeed()

        if((busID == '2.0') & (enitalB2 > 1)):

            busId2.setBusLocation(float(data_disc["feeds"][1]["field1"]),float(data_disc["feeds"][1]["field2"]))
            distanceFormGoal = busId2.distanceFormGoal(busStopPoint[0],busStopPoint[1])
            speed = busId2.readSpeed()

        if((busID == '1.0') & (enitalB1 == 1)):

            enitalB1 = 2

        if((busID == '2.0') & (enitalB2 == 1)):

            enitalB2 = 2
            
        estimateTimeToBusStop = (distanceFormGoal/speed) * 60

        bc.mine_block("Bus ID :" + str(busID) + 
                      ",Station ID :" + str(stationID) + 
                      ",Distance to bus stop :" + str(distanceFormGoal) +
                      ",Speed :" + str(speed) + 
                      ",Estimate time to bus stop :"+ str(estimateTimeToBusStop)
                     )
        dataForAdd = [bc.chain[len(bc.chain)-1]["index"],
                     bc.is_chain_valid(),
                     busID,
                     stationID,
                     distanceFormGoal,
                     speed,
                     estimateTimeToBusStop,
                     bc.chain[len(bc.chain) - 1]["previous_hash"]]

        addData(dataForAdd)

        print(bc.chain[len(bc.chain)-1])# print the current block

    time.sleep(15)