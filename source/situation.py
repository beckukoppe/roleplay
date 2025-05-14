import util as util
from llm import CMD

class Situation:
    def __init__(self, name, enviroment, gamemaster):
        self.name = name
        self.enviroment = enviroment
        self.characters = []
        self.ready = []
        self.leaving = []
        self.responce = None
        self.end = False
        self.transcript = ""
        self.gamemaster = gamemaster

    def addCharacter(self, character):
        self.characters.append(character)

    def __info(self, who, info):
        self.__sysbrodcast("#INFO(" + who + " " + info + ")")

    def __scenario(self, text):
        self.__sysbrodcast("#SCENARIO(" + text + ")")

    def __usay(self, text):
        self.__userbrodcast("#PLAYERSAY(" + text + ")")

    def __ssay(self, index, name, text):
        message =  "#SAY(" + name + "; " + text + ")"
        self.transcript += message
        #speaker = self.characters[index]
        #speaker.llm.llmlisten("#YOU(" + name + "; " + text + ")")
        print(message)
        for i in range(0, len(self.characters)):
            if (i == index): continue
            c = self.characters[i]
            c.llm.syslisten(message)

    def __userbrodcast(self, message):
         self.transcript += message
         print(message)

         for i in range(0, len(self.characters)):
            c = self.characters[i]
            c.llm.userlisten(message)

    def __sysbrodcast(self, message):
         self.transcript += message
         print(message)

         for i in range(0, len(self.characters)):
            c = self.characters[i]
            c.llm.system(" THE CURRENT SITUATION: " + message)

    def isEnd(self):
        return self.end
    
    def leave(self):
        self.gamemaster.summarize(self.transcript)

        response = self.gamemaster.ask([CMD.NOTHING, CMD.OBJECTIVE], "#NEWOBJECTIVES - answer with #NOTHING or the objective syntax. But only when there was a concrete objective!")
        print(response)
        assert len(response) > 0, "LLM ERROR"
        for cmd in response:
            if(cmd.get("command") == "OBJECTIVE"):
                self.gamemaster.addObjective(cmd)

    def enter(self):
        names = ""
        for c in self.characters:
            names += c.getName() + ","

        scenario = self.gamemaster.getScenario(self.name, names)
        self.__scenario(scenario)

    def __usersay(self, text):
        self.__usay(text)

        for i in range(0, len(self.characters)):
            c = self.characters[i]

            response = c.llm.usercall([CMD.NOTHING, CMD.FORCEEND, CMD.PROPOSEEND, CMD.SAY], "Do you want to perform an action?")
            assert len(response) > 0, "LLM ERROR"
            for cmd in response:
                if(cmd.get("command") == "SAY"):
                    self.__speakersay(i, cmd.get("arg0"))
                if(cmd.get("command") == "FORCEEND"):
                    self.__info(c.getName(), "left the conversation")
                    self.leaving.append(c)
                if(cmd.get("command") == "PROPOSEEND"):
                    self.__info(c.getName(), "has nothing more to say")
                    self.ready.append(c)

    def __speakersay(self, index, text):
        talking = self.characters[index]
        self.__ssay(index, talking.getName(), text)

        for i in range(0, len(self.characters)):
            if index == i: continue
            c = self.characters[i]

            #c.syslisten("#SAY(" + talking.getName() + ", " + text + ")")
            response = c.llm.usercall([CMD.NOTHING, CMD.FORCEEND, CMD.PROPOSEEND], "Do you want to perform an action?")
            assert len(response) > 0, "LLM ERROR"
            for cmd in response:
                if(cmd.get("command") == "FORCEEND"):
                    self.__info(c.getName(), "left the conversation")
                    self.leaving.append(c)
                elif(cmd.get("command") == "PROPOSEEND"):
                    self.__info(c.getName(), "has nothing more to say")
                    self.ready.append(c)
                else:
                    i += 1

    def update(self):
        if(self.end == True):
            return

        while len(self.leaving) > 0:
            c = self.leaving[0]
            #c.llm.memorize(self.transcript)
            util.try_remove(self.characters, c)
            self.leaving.remove(c)

        for c in self.ready:
            util.try_remove(self.characters, c)

        if(len(self.characters) == 0):
            if(len(self.ready) > 0 and not self.userEndConversation()):
                self.characters.extend(self.ready)
                self.ready.clear()
                self._userSaySomething()
                return
            else:
                self.end = True
                #for c in self.ready:
                    #c.llm.memorize(self.transcript)
                return

        self._speakerSaySomething()

        if(len(self.characters) == 0):
            if(len(self.ready) > 0 and not self.userEndConversation()):
                self.characters.extend(self.ready)
                self.ready.clear()
                self._userSaySomething()
                return
            else:
                self.end = True
                #for c in self.ready:
                    #c.llm.memorize(self.transcript)
                return

        self._userSaySomething()

    def userEndConversation(self):
        print("Do you want to end this conversation? [Y/n]")
        choice = input("Enter your choice: ")
        if choice == "n":
            return False
        else:
            return True

    def _userSaySomething(self):
        user_input = input("(#END/#NOMORE) Say: ")
        if(user_input.startswith("#END")):
            self.__info("USER", "left conversation")
            self.end = True
        elif(user_input.startswith("#NOMORE")):
            self.__info("USER", "has nothing more to say")
        else:
            self.__usersay(user_input)

    def _speakerSaySomething(self):
        i = 0
        while i < len(self.characters): 
            c = self.characters[i]
            response = c.llm.usercall([CMD.NOTHING, CMD.FORCEEND, CMD.PROPOSEEND, CMD.SAY], "Do you want to perform an action?")
            assert len(response) > 0, "LLM ERROR"
            someone = False
            for cmd in response:
                if(cmd.get("command") == "SAY"):
                    self.__speakersay(i, cmd.get("arg0"))
                    someone = True
                if(cmd.get("command") == "FORCEEND"):
                    print(c.getName() + " left the conversation")
                    self.transcript += c.getName() + " left the conversation"
                    self.characters.pop(i)
                    someone = True
                if(cmd.get("command") == "PROPOSEEND"):
                    print(c.getName() + " has nothing more to say")
                    self.transcript += c.getName() + " has nothing more to say"
                    self.characters.pop(i)
                    self.ready.append(c)
                    someone = True

            if(someone):
                return
            
            i += 1
