import util as util

from llm import LLM
from llm import CMD
from Logger import Logger
from datetime import datetime, timedelta
from objective import Objective

class Gamemaster:
    def __init__(self, preperation, enviroment):
        self.__llm = LLM(LLM.GAMEMASTER_URL, util.readFile("prompt/gamemaster.txt"), Logger("Gamemaster"))
        self.__llm.syslisten(preperation)
        self.enviroment = enviroment
        self.objectives = []

    def getScenario(self, scenario_name, participants):
        response = self.__llm.syscall([CMD.SCENARIO,], f"provide scenario for {scenario_name} with {participants}")
        assert len(response) > 0, "Gamemaster response is invalid"
        return response[0].get("arg0")
    
    def call(self, message, context=None):
        if(None == context):
            context = ""
        return self.__llm.syscall(message, "#CURRENTTIME{" + self.enviroment.getTime() + "}" + context)

    def ask(self, message, context=None):
        if(None == context):
            context = ""
        return self.__llm.sysask(message, "#CURRENTTIME{" + self.enviroment.getTime() + "}" + context)
    
     def listen(self, message, context=None):
        if(None == context):
            context = ""
        return self.__llm.syslisten(message, "#CURRENTTIME{" + self.enviroment.getTime() + "}" + context)

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