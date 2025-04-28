from story import Story
from situation import Situation

REPORTER_COUNT = 2

class Game:
    def __init__(self):
        print("Started game preperation...")
        self._shouldStop = False

        story = Story()

        self.enviroment = story.prepareEnviroment()

        self.office = Situation("office", self.enviroment)
        self.speak_hostage_taker = Situation("speak_hostage_taker", self.enviroment)
        self.pressconference = Situation("pressconference", self.enviroment)

        self.hostage_taker = story.prepareHostageTaker()
        self.speak_hostage_taker.addCharacter(self.hostage_taker)

        self.reporters = []
        for i in range(REPORTER_COUNT):
            reporter = story.prepareReporter()
            self.reporters.append(reporter)
            self.pressconference.addCharacter(reporter)

        self.gamemaster = story.prepareGamemaster()

        self.situation = self.office

        print("Finished game preperation...")

    def update(self):
        print("Time: " + self.enviroment.getTime())

        if(self.situation.isEnd()):
            self.offerSituations()
        else:
            self.situation.update()

        self.enviroment.tick();

        self.gamemaster.update()
        #TODO prossesGameMasterCommands

    def shouldStop(self):
        return self._shouldStop
    
    def enterSituation(self):
        print("talk")
    
    def offerSituations(self):
        while True:
            print("=== Main Menu ===")
            print("1. Speak with hostage-taker")
            print("2. Hold press-conference")
            print("3. Wait and do nothing")
            print("0. End Game")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.situation = self.speak_hostage_taker
                return
            elif choice == "2":
                self.situation = self.pressconference
                return
            elif choice == "3":
                self.enviroment.skip(5)
                return
            elif choice == "0":
                print("\nGoodbye!")
                self.shouldStop = True
                return
            else:
                print("\nInvalid choice. Please try again.\n")
