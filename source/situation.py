class Situation:
    def __init__(self, name, enviroment):
        self.name = name
        self.enviroment = enviroment
        self.characters = []
        self.ready = []
        self.responce = None
        self.end = False

    def addCharacter(self, character):
        self.characters.append(character)

    def isEnd(self):
        return self.end
    
    def enter(self):
        count = "#COUNT(" + str(len(self.characters) + len(self.ready)) + ")"
        for i in range(0, len(self.characters)):
            c = self.characters[i]
            response = c.llm.call(count + "#INFO{entering new conversation}")

    def usersay(self, formated_text):
        for i in range(0, len(self.characters)):
            c = self.characters[i]
            response = c.llm.call(formated_text)
            assert len(response) > 0, "LLM ERROR"
            for cmd in response:
                if(cmd.get("command") == "SAY"):
                    self.speakersay(i, cmd.get("data"))
                if(cmd.get("command") == "FORCEEND"):
                    print(c.getName() + " left the conversation")
                    self.characters.remove(c)
                if(cmd.get("command") == "PROPOSEEND"):
                    print(c.getName() + " has nothing more to say")
                    self.characters.remove(c)
                    self.ready.append(c)


    def speakersay(self, index, text):
        c = self.characters[index]

        print(c.getName() + " says: " + text)
        for i in range(0, len(self.characters)):
            c.llm.listen("SPEAKERSAY(" + c.getName() + "){" + text + "}");

    def update(self):
        if(len(self.characters) == 0):
            if(len(self.ready) > 0 and self.userEndConversation()):
                self.characters.extend(self.ready)
                self.ready.clear()
                self._userSaySomething()
                return
            else:
                self.end = True
                print("leaving situation...")
                return

        self._speakerSaySomething()

        self._userSaySomething()

    def userEndConversation(self):
        print("Do you want to end this conversation? [Y/n]")
        choice = input("Enter your choice: ")
        if choice == "n":
            return False
        else:
            return True

    def _userSaySomething(self):
        user_input = input("Say: ")
        if(user_input.startswith("#")):
            self.usersay(user_input)
        else:
            self.usersay("USERSAY{" + user_input + "}")

    def _speakerSaySomething(self):
        i = 0
        while i < len(self.characters): 
            c = self.characters[i]
            response = c.llm.call("#SYSTEM{Do you want to perform an action? If so respond with the corresponding action syntax. If you dont have or dont want to say anything respond with '#NOTHING'} (this is a systhem message, not a user message!)")
            assert len(response) > 0, "LLM ERROR"
            found = False
            for cmd in response:
                if(cmd.get("command") == "SAY"):
                    self.speakersay(i, cmd.get("data"))
                    found = True
                if(cmd.get("command") == "FORCEEND"):
                    print(c.getName() + " left the conversation")
                    self.characters.pop(i)
                    found = True
                if(cmd.get("command") == "PROPOSEEND"):
                    print(c.getName() + " has nothing more to say")
                    self.characters.pop(i)
                    self.ready.append(c)
                    found = True

            if(found):
                return
            
            i += 1
