from Logger import Logger

class Event:
    def __init__(self, name, description, time):
        self.name = name
        self.description = description
        self.time = time
        self.happened = False

    def isNow(self, time):
        return time >= self.time and not self.happened
    
    def happen(self):
        self.happened = True
       
