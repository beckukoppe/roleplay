import util as util

from llm import LLM
from llm import CMD

class Gamemaster:
    def __init__(self, preperation, enviroment):
        self.__llm = LLM(LLM.GAMEMASTER_URL, util.readFile("prompt/gamemaster.txt"))
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

    def summarize(self, conversation):
        self.__llm.sysask([CMD.SUMMARY,], "summarize the following conversation. think about what that means for the story: " + conversation)

    def addObjective(self, command):
        print(command.get("command"))
        print(command.get("arg0"))
        print(command.get("arg1"))