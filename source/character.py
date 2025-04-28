import util as util

from llm import LLM

class Character:
    def __init__(self, prompt_name, name, definition):
        self.llm = LLM(LLM.SPEAKER_URL, util.readFile("prompt/speaker_llm.txt"), LLM.SPEAKER_COMMANDS)
        self.llm.briefing(util.readFile("prompt/" + prompt_name))
        self.name = name

    def getName(self):
        return self.name
        
    def wannaTalk(self, situation):
        return False
    

        
