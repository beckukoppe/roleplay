from datetime import datetime, timedelta

class Environment:
    def __init__(self, start_time):
        try:
            self.time = datetime.strptime(start_time, "%H:%M")
        except ValueError:
            raise ValueError("Start time must be in 'HH:MM' 24-hour format.")

    def tick(self):
        self.time += timedelta(minutes=1)

    def getTime(self):
        return self.time.strftime("%H:%M")

    def skip(self, minutes_to_skip):
        if not isinstance(minutes_to_skip, int) or minutes_to_skip < 0:
            raise ValueError("minutes_to_skip must be a non-negative integer.")
        self.time += timedelta(minutes=minutes_to_skip)
