from story import Story
from situation import Situation
from event import Event
from action import Action

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

        self.situation = self.officeEvent
        self.enviroment.tick();
    
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
            print("=== Main Menu ===")

            # Statische Aktionsliste
            actions = [
                Action("1", "Wait and do nothing", lambda: self.enviroment.skip(5)),
                Action("0", "End Game", self.endGame)
            ]

            letter = 'a'

            response = self.gamemaster.ask([["NONE"], ["SPEAKTOHOSTAGETAKER"], ["HOLDPRESSCONFERENCE"], ["DYNAMICOPERATION", "name", "description"]], "What options does the user have? what actions can je do?  which does the current situation allow him to do?")
            assert len(response) > 0, "LLM ERROR"
            for cmd in response:                    
                if(cmd.get("command") == "SPEAKTOHOSTAGETAKER"):
                    actions.append(Action(letter, "Speak with hostage-taker", lambda: self.startSituation("speak_hostage_taker", [self.hostage_taker])));
                if(cmd.get("command") == "HOLDPRESSCONFERENCE"):
                    actions.append(Action(letter, "Hold press-conference", lambda: self.startSituation("press_conference", self.reporters.copy())));
                if(cmd.get("command") == "DYNAMICOPERATION"):
                    actions.append(Action(letter, cmd.get("arg0", lambda: self.startSituation("arg0", self.reporters.copy())));

                letter += 1

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