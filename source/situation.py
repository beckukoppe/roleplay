import util as util

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

    def isEnd(self):
        return self.end
    
    def leave(self):
        self.gamemaster.sumup(self.transcript)

        response = self.gamemaster.ask("#NEWOBJECTIVES - answer with #NOTHING or the objective syntax!")
        print(response)
        assert len(response) > 0, "LLM ERROR"
        for cmd in response:
            if(cmd.get("command") == "OBJECTIVE"):
                self.gamemaster.addObjective(cmd)

    def enter(self):
        names = ""
        for c in self.characters:
            names += c.getName() + ","

        #count = "#COUNT(" + str(len(self.characters) + len(self.ready) + 1) + ")"
        #self.transcript += "#INFO{conversation with "  + count + " participants: " + names + "}"
        scenario = self.gamemaster.getScenario(self.name, names)
        self.transcript += "\n#SCENARIO{" + scenario + "}"

    def usersay(self, formated_text):
        for i in range(0, len(self.characters)):
            c = self.characters[i]
            response = c.llm.ask(formated_text, "(you are not allowed to say something. end, propose or nothing!) #CURRENTCONVERSATION {" + self.transcript + "}")
            assert len(response) > 0, "LLM ERROR"
            for cmd in response:
                if(cmd.get("command") == "FORCEEND"):
                    print(c.getName() + " left the conversation")
                    self.transcript += c.getName() + " left the conversation"
                    self.leaving.append(c)
                if(cmd.get("command") == "PROPOSEEND"):
                    print(c.getName() + " has nothing more to say")
                    self.transcript += c.getName() + " has nothing more to say"
                    self.ready.append(c)

        self.transcript += formated_text

    def speakersay(self, index, text):
        talking = self.characters[index]
        print(talking.getName() + " says: " + text)
        
        formated_text = "#SPEAKERSAY(" + talking.getName() + "){" + text + "}"

        for i in range(0, len(self.characters)):
            if index == i: continue
            c = self.characters[i]
            response = c.llm.ask(formated_text, "(you are not allowed to say something. end, propose or nothing!) #CURRENTCONVERSATION {" + self.transcript + "}")

            assert len(response) > 0, "LLM ERROR"
            for cmd in response:
                if(cmd.get("command") == "FORCEEND"):
                    print(c.getName() + " left the conversation")
                    self.transcript += c.getName() + " left the conversation"
                    self.leaving.append(c)
                elif(cmd.get("command") == "PROPOSEEND"):
                    print(c.getName() + " has nothing more to say")
                    self.transcript += c.getName() + " has nothing more to say"
                    self.ready.append(c)
                else:
                    i += 1

        self.transcript += formated_text

    def update(self):
        while len(self.leaving) > 0:
            c = self.leaving[0]
            c.llm.memorize(self.transcript)
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
                for c in self.ready:
                    c.llm.memorize(self.transcript)
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
                for c in self.ready:
                    c.llm.memorize(self.transcript)
                return

        self._userSaySomething()

    def userEndConversation(self):
        print("Do you want to end this conversation? [Y/n]")
        choice = input("Enter your choice: ")
        if choice == "n":
            return Falseleast
        else:
            return True

    def _userSaySomething(self):
        user_input = input("Say: ")
        if(user_input.startswith("#")):
            self.usersay(user_input)
        else:
            self.usersay("#USERSAY{" + user_input + "}")

    def _speakerSaySomething(self):
        i = 0
        while i < len(self.characters): 
            c = self.characters[i]
            response = c.llm.ask("#YOURTURN(do you want to perform an action (maybe say something, or leave)? if not #NOTHING)", "#CURRENTCONVERSATION {" + self.transcript + "}")
            assert len(response) > 0, "LLM ERROR"
            someone = False
            for cmd in response:
                if(cmd.get("command") == "SAY"):
                    print(cmd)
                    self.speakersay(i, cmd.get("data"))
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
