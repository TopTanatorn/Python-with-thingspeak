import numpy as np

R = 6373.0 # world radius

class Bus:
    
    
    def __init__(self, lat, lon):
        
        self.lat = lat
        self.lon = lon
        self.previousLat = lat
        self.previousLon = lon
        
    def setBusLocation(self, newLat, newLon):
        
        self.previousLat = self.lat
        self.previousLon = self.lon
        self.lat = newLat
        self.lon = newLon
        
    def getBusLocation(self):
        
        return self.lat, self.lon, self.previousLat, self.previousLon
        
    def distanceFormGoal(self, lat, lon):
        
        lat1 = np.radians(self.lat)
        lon1 = np.radians(self.lon)

        lat2 = np.radians(lat)
        lon2 = np.radians(lon)
        #find difference between point 1 and point 2
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        distance = R * c
        
        return distance
    
    def readSpeed(self):
        
        lat1 = np.radians(self.lat) 
        lon1 = np.radians(self.lon)

        lat2 = np.radians(self.previousLat)
        lon2 = np.radians(self.previousLon)
        #find difference between point 1 and point 2
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        distance = R * c
        speed = (distance*3600)/60 #km/hr send interval 60 sec
        
        return speed
        