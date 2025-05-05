import util as util

from enviroment import Environment
from character import Character
from gamemaster import Gamemaster
from llm import LLM

class Story:
    def __init__(self):
        self.story_llm = LLM(LLM.STORY_URL, util.readFile("prompt/story_llm.txt"), LLM.STORY_COMMANDS)
        self.story = self.story_llm.call("Generate the story (brief) as '#STORY{content}'")
        print("story...")
        
    def prepareHostageTaker(self):
        name = self.story_llm.call("Provide the name for the hostage taker as '#NAME{content}'")
        assert len(name) > 0, "LLM ERROR"
        definition = self.story_llm.call("Generate the character definition for the hostage-taker as '#CHARACTER{content}'. brief it so that it knows that it is the hostage taker!")
        assert len(definition) > 0, "LLM ERROR"
        character = Character("hostage_taker.txt", name[0].get("data"), definition[0].get("data"))
        print("hostage-taker...")
        return character
    
    def prepareReporter(self):
        name = self.story_llm.call("Provide the name for only the next Reporter as '#NAME{content}'. No more no less!")
        assert len(name) > 0, "LLM ERROR"
        definition = self.story_llm.call("Generate the character definition for the reporter as '#CHARACTER{content}'")
        assert len(definition) > 0, "LLM ERROR"
        character = Character("reporter.txt", name[0].get("data"), definition[0].get("data"))
        print("reporter...")
        return character
    
    def prepareEnviroment(self):
        time = self.story_llm.call("Give the start time in 24-hour format as '#TIME{HH:MM}'")
        assert len(time) > 0, "LLM ERROR"
        enviroment = Environment(time[0].get("data"))
        print("enviroment...")
        return enviroment
        
    def prepareGamemaster(self, enviroment):
        preperation = self.story_llm.call("Generate the preperation for the as '#GAMEMASTER{content}'")
        assert len(preperation) > 0, "LLM ERROR"
        gamemaster = Gamemaster(preperation[0].get("data"), enviroment)
        print("gamemaster...")
        return gamemaster