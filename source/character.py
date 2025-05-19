import util as util

from llm import LLM
from Logger import Logger

class Character:
    def __init__(self, prompt_name, name, definition):
        self.llm = LLM(LLM.SPEAKER_URL, Logger(name))
        self.name = name

        self.llm.syslisten(util.readFile("prompt/speaker_llm.txt"))
        self.llm.syslisten("YOUR ROLE: " + util.readFile("prompt/" + prompt_name))
        self.llm.syslisten("YOUR NAME: " + self.name)
        self.llm.syslisten("YOUR CHARACTER DESCRIPTION: " + definition)
    
    def getName(self):
        return self.name