import util as util

from llm import LLM

class Gamemaster:
    def __init__(self, preperation, enviroment):
        self.__llm = LLM(LLM.GAMEMASTER_URL, util.readFile("prompt/gamemaster.txt"), LLM.GAMEMASTER_COMMANDS)
        self.__llm.listen(preperation)
        self.enviroment = enviroment
        self.objectives = []

    def getScenario(self, scenario_name, participants):
        response = self.__llm.call(f"#SCENARIO({scenario_name},{participants})")
        assert len(response) > 0, "Gamemaster response is invalid"
        return response[0].get("data")
    
    def call(self, message, context=None):
        if(None == context):
            context = ""
        return self.__llm.call(message, "#CURRENTTIME{" + self.enviroment.getTime() + "}" + context)

    def ask(self, message, context=None):
        if(None == context):
            context = ""
        return self.__llm.ask(message, "#CURRENTTIME{" + self.enviroment.getTime() + "}" + context)

    def sumup(self, conversation):
        self.__llm.sumup(conversation)

    def update(self, summary):
        self.__llm.listen(summary)

    def addObjective(self, command):
        print(command.get("command"))
        print(command.get("data"))
        print(command.get("param"))