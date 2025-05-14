import util as util

from llm import LLM
from Logger import Logger

class Character:
    def __init__(self, prompt_name, name, definition):
        self.llm = LLM(LLM.SPEAKER_URL, util.readFile("prompt/speaker_llm.txt"), Logger(name))
        self.llm.system(" YOUR ROLE: " + util.readFile("prompt/" + prompt_name))
        self.name = name
        self.llm.system(" YOUR NAME: " + self.name)
        self.llm.system(" YOUR CHARACTER DESCRIPTION: " + definition)

    def getName(self):
        return self.name
        
    def wannaTalk(self, situation):
        return False
    

        
