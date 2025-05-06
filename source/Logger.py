import os
from datetime import datetime
import util

class Logger:
    def __init__(self, name):
        self.name = name
        self.log_dir = "log"
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def _write_log(self, filename, content):
        path = os.path.join(self.log_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(content))

    def log(self, history, response):
        timestamp = self._get_timestamp()
        filename = f"{self.name}_log_{timestamp}.txt"
        content = f"{util.formatted_history(history)}\nResponse:\n{response}"
        self._write_log(filename, content)