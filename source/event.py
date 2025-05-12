from Logger import Logger

class Event:
    def __init__(self, name, description, time):
        self.name = name
        self.description = description
        self.time = time

    def isNow(self, time):
        return time == self.time
       
