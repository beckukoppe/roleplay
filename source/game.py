from story import Story
from situation import Situation

REPORTER_COUNT = 2

class Game:
    def __init__(self):
        print("Started game preperation...")
        self._shouldStop = False

        story = Story()
        self.gamemaster = story.prepareGamemaster()

        self.enviroment = story.prepareEnviroment()

<<<<<<< HEAD
        self.office = Situation("office", self.enviroment)
=======
        self.office = Situation("office", self.enviroment, self.gamemaster)
        self.speak_hostage_taker = Situation("speak_with_hostage_taker", self.enviroment, self.gamemaster)
        self.pressconference = Situation("pressconference", self.enviroment, self.gamemaster)
>>>>>>> 07535d6ee4e9687f33f4d372175b32d93b41d1b8

        self.hostage_taker = story.prepareHostageTaker()

        self.reporters = []
        for i in range(REPORTER_COUNT):
            reporter = story.prepareReporter()
            self.reporters.append(reporter)


        self.situation = self.office

        print("Finished game preperation...")

    def update(self):
        print("Time: " + self.enviroment.getTime())

        if(self.situation.isEnd()):
            self.offerSituations()
        else:
            self.situation.update()

        self.enviroment.tick();

        #self.gamemaster.update()
        #TODO prossesGameMasterCommands

    def shouldStop(self):
        return self._shouldStop

    
    def offerSituations(self):
        while True:
            print("=== Main Menu ===")
            print("1. Speak with hostage-taker")
            print("2. Hold press-conference")
            print("3. Wait and do nothing")
            print("0. End Game")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.situation.leave()
                self.situation = Situation("speak_hostage_taker", self.enviroment)
                self.situation.addCharacter(self.hostage_taker)
                self.situation.enter()
                return
            elif choice == "2":
                self.situation.leave()
                self.situation = Situation("pressconference", self.enviroment)
                for r in self.reporters:
                    self.situation.addCharacter(r)
                self.situation.enter()
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
