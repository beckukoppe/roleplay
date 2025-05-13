from story import Story
from situation import Situation
from event import Event
from action import Action
from operation import Operation

REPORTER_COUNT = 2

class Game:
    def __init__(self):
        print("Started game preperation...")
        self._shouldStop = False

        story = Story()

        self.enviroment = story.prepareEnviroment()

        self.gamemaster = story.prepareGamemaster(self.enviroment,)

        self.office = Situation("office", self.enviroment, self.gamemaster)
        self.office.transcript = "#INFO{nothing happended}"

        self.hostage_taker = story.prepareHostageTaker()

        self.reporters = []
        for i in range(REPORTER_COUNT):
            reporter = story.prepareReporter()
            self.reporters.append(reporter)

        self.situation = self.office
        self.enviroment.tick();
    
        self.staged_events = []
    

    def update(self):
        print("Time: " + self.enviroment.getTime())

        if(self.situation.isEnd()):
            self.offerSituations()
        else:
            if(self.situation != None):
                self.situation.update()

        self.enviroment.tick();

        #self.gamemaster.update()
        #TODO prossesGameMasterCommands

        # EVENT
        for event in self.staged_events:
            if(event.isNow()):
                event.happen()
                self.gamemaster.listen("#INFO(" + event.name + " - " + event.description + " just happened)")

        #self.gamemaster.update()
        #TODO prossesGameMasterCommands

        # OBJECTIVE
        #for o in self.objectives:
        #    response = self.gamemaster.llm.ask();
        #    assert len(response) > 0, "LLM ERROR"
        #        for cmd in response:
        #            if(cmd.get("command") == "NOTHING"):
        #                continue
        #            if(cmd.get("command") == "FORCEEND"):
        #                
        #            if(cmd.get("command") == "PROPOSEEND"):
                        

    def shouldStop(self):
        return self._shouldStop

    
    def offerSituations(self):
        if self.situation is not None and self.situation != self.office:
            self.situation.leave()

        while True:

            # Statische Aktionsliste
            actions = [
                Action("1", "Wait and do nothing", lambda: self.enviroment.skip(5)),
                Action("0", "End Game", self.endGame)
            ]

            letter = 'a'

            response = self.gamemaster.ask([["NONE"], ["SPEAKTOHOSTAGETAKER"], ["HOLDPRESSCONFERENCE"], ["DYNAMICOPERATION", "name", "description", "agent_name"]], "What options does the user have? what actions can je do?  which does the current situation allow him to do? Give all possible options! But be aware that your answer is interpreted. so no extra commands other than the one for allowing options. #NONE is a command only to use when nothing is possible for the player to do right now. replace the <...> with a text string that coresponds to it")
            assert len(response) > 0, "LLM ERROR"
            for cmd in response:                    
                if(cmd.get("command") == "SPEAKTOHOSTAGETAKER"):
                    actions.append(Action(letter, "Speak with hostage-taker", lambda: self.startSituation("speak_hostage_taker", [self.hostage_taker])));
                if(cmd.get("command") == "HOLDPRESSCONFERENCE"):
                    actions.append(Action(letter, "Hold press-conference", lambda: self.startSituation("press_conference", self.reporters.copy())));
                if(cmd.get("command") == "DYNAMICOPERATION"):
                    name = cmd.get("arg0")
                    description = cmd.get("arg1")
                    agent_name = cmd.get("arg2")
                    print(cmd)
                    op = Operation(description, agent_name, self.gamemaster)
                    actions.append(Action(letter, name, lambda: op.start()));

                letter = chr(ord(letter) + 1)

            print("=== Main Menu ===")

            for a in actions:
                print(f"{a.id}. {a.description}")

            print("=================")

            choice = input("Enter your choice: ").strip()

            for a in actions:
                if a.id == choice:
                    a.callback()
                    return

            print("\nInvalid choice. Please try again.\n")

    def startSituation(self, name, characters):
        self.situation = Situation(name, self.enviroment, self.gamemaster)
        for c in characters:
            self.situation.addCharacter(c)
        self.situation.enter()

    def endGame(self):
        print("\nGoodbye!")
        self._shouldStop = True