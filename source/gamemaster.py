import util as util

from llm import LLM
from llm import CMD
from Logger import Logger
from datetime import datetime, timedelta
from objective import Objective

class Gamemaster:
    def __init__(self, preperation, enviroment):
        self.__llm = LLM(LLM.GAMEMASTER_URL, Logger("Gamemaster"))
        self.enviroment = enviroment
        self.objectives = []

        self.__llm.syslisten(util.readFile("prompt/gamemaster.txt"))
        self.__llm.syslisten("You will now receive the info story prompt: " + preperation)

    def getScenario(self, scenario_name, participants):
        response = self.__llm.usercall([CMD.SCENARIO,], f"Now provide the '{scenario_name}' scenario with '{participants}'")
        assert len(response) > 0, "Gamemaster response is invalid"
        return response[0].get("arg0")
    
    def call(self, allowed, message, context=None):
        if(None == context):
            context = ""
        return self.__llm.syscall(allowed, message, "#CURRENTTIME{" + self.enviroment.getTime() + "}" + context)

    def ask(self, allowed, message, context=None):
        if(None == context):
            context = ""
        return self.__llm.syscall(allowed, message, "#CURRENTTIME{" + self.enviroment.getTime() + "}" + context)
    
    def listen(self, message):
        return self.__llm.syslisten(message)

    def summarize(self, conversation):
        self.__llm.sysask([CMD.SUMMARY,], "summarize the following conversation. think about what that means for the story: " + conversation)

    def addObjective(self, command):
        name = command.get("arg0")
        description = command.get("arg1")
        time = command.get("arg2")

        try:
            ftime = datetime.strptime(time, "%H:%M")
        except ValueError:
            raise ValueError("LLM FAILED: Start time must be in 'HH:MM' 24-hour format.")
        
        ob = Objective(name, description, ftime)

        self.objectives.append(ob)