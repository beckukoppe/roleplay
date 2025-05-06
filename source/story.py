import util as util

from enviroment import Environment
from character import Character
from gamemaster import Gamemaster
from llm import LLM
from Logger import Logger


class Story:
    def __init__(self):
        self.story_llm = LLM(LLM.STORY_URL, util.readFile("prompt/story_llm.txt"))
        self.story = self.story_llm.syscall([["STORY", "content text"],], "Generate the story (brief)", )
        print("story...")
        
    def prepareHostageTaker(self):
        name = self.story_llm.syscall([["NAME", "first_name seccond_name"],], "Provide the name for the hostage taker")
        assert len(name) > 0, "LLM ERROR"
        definition = self.story_llm.syscall([["CHARACTER", "description text"],], "Generate the character definition for the hostage-taker. brief it so that it knows that it is the hostage taker!")
        assert len(definition) > 0, "LLM ERROR"
        character = Character("hostage_taker.txt", name[0].get("arg0"), definition[0].get("arg0"), Logger("hostage_taker"))
        print("hostage-taker...")
        return character
    
    def prepareReporter(self):
        name = self.story_llm.syscall([["NAME", "first_name seccond_name"],], "Provide the name for only the next Reporter")
        assert len(name) > 0, "LLM ERROR"
        definition = self.story_llm.syscall([["CHARACTER", "description text"],], "Generate the character definition for the reporter")
        assert len(definition) > 0, "LLM ERROR"
        character = Character("reporter.txt", name[0].get("arg0"), definition[0].get("arg0"), Logger("reporter"))
        print("reporter...")
        return character
    
    def prepareEnviroment(self):
        time = self.story_llm.syscall([["TIME", "HH:MM"],], "Give the start time in 24-hour format")
        assert len(time) > 0, "LLM ERROR"
        enviroment = Environment(time[0].get("arg0"))
        print("enviroment...")
        return enviroment
        
    def prepareGamemaster(self, enviroment):
        preperation = self.story_llm.syscall([["GAMEMASTER", "content text"],], "Generate the preperation for the gamemaster llm. tell it your story plans. it will oversee the actor actions")
        assert len(preperation) > 0, "LLM ERROR"
        gamemaster = Gamemaster(preperation[0].get("arg0"), enviroment)
        print("gamemaster...")
        return gamemaster