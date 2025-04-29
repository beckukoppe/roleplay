import util as util

from llm import LLM

class Gamemaster:
    def __init__(self, preperation):
        self.llm = LLM(LLM.GAMEMASTER_URL, util.readFile("prompt/gamemaster.txt"), LLM.GAMEMASTER_COMMANDS)
        self.llm.listen(preperation)

    def getScenario(self, scenario_name, participants):
        response = self.llm.call(f"#SCENARIO({scenario_name},{participants})")
        print(response)
        assert len(response) > 0, "Gamemaster response is invalid"
        return response[0].get("data")

    def update(self, summary):
        self.llm.listen(summary)