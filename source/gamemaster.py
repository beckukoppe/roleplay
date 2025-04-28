import util as util

from llm import LLM

class Gamemaster:
    def __init__(self, preperation):
        self.llm = LLM(LLM.GAMEMASTER_URL, util.readFile("prompt/gamemaster.txt"), LLM.GAMEMASTER_COMMANDS)

    def update(self):
        print("update")