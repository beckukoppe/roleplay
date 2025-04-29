class Situation:
    def __init__(self, name, enviroment):
        self.name = name
        self.enviroment = enviroment
        self.characters = []
        self.ready = []
        self.responce = None
        self.end = False
        self.transcript = ""

    def addCharacter(self, character):
        self.characters.append(character)

    def isEnd(self):
        return self.end
    
    def leave(self):
        print("leaving situation")
    
    def enter(self):
        count = "#COUNT(" + str(len(self.characters) + len(self.ready) + 1) + ")"
        self.transcript += count 

    def usersay(self, formated_text):
        for i in range(0, len(self.characters)):
            c = self.characters[i]
            print(self.transcript)
            response = c.llm.call(formated_text, "#CURRENTCONVERSATION" + self.transcript + "}")
            self.transcript += formated_text
            assert len(response) > 0, "LLM ERROR"
            for cmd in response:
                if(cmd.get("command") == "FORCEEND"):
                    print(c.getName() + " left the conversation")
                    self.characters.remove(c)
                if(cmd.get("command") == "PROPOSEEND"):
                    print(c.getName() + " has nothing more to say")
                    self.characters.remove(c)
                    self.ready.append(c)

    def speakersay(self, index, text):
        talking = self.characters[index]
        print(talking.getName() + " says: " + text)
        
        i = 0
        while i < len(self.characters): 
            c = self.characters[i]
            print(self.transcript)
            formated_text = "#SPEAKERSAY(" + talking.getName() + "){" + text + "}"
            response = c.llm.call(formated_text, "#CURRENTCONVERSATION" + self.transcript + "}")
            self.transcript += formated_text

            assert len(response) > 0, "LLM ERROR"
            for cmd in response:
                if(cmd.get("command") == "FORCEEND"):
                    print(c.getName() + " left the conversation")
                    self.characters.remove(c)
                elif(cmd.get("command") == "PROPOSEEND"):
                    print(c.getName() + " has nothing more to say")
                    self.characters.remove(c)
                    self.ready.append(c)
                else:
                    i += 1

    def update(self):
        if(len(self.characters) == 0):
            if(len(self.ready) > 0 and not self.userEndConversation()):
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
            print(self.transcript)
            response = c.llm.ask("#YOURTURN", "#CURRENTCONVERSATION" + self.transcript + "}")
            assert len(response) > 0, "LLM ERROR"
            someone = False
            for cmd in response:
                if(cmd.get("command") == "SAY"):
                    self.speakersay(i, cmd.get("data"))
                    someone = True
                if(cmd.get("command") == "FORCEEND"):
                    print(c.getName() + " left the conversation")
                    self.characters.pop(i)
                    someone = True
                if(cmd.get("command") == "PROPOSEEND"):
                    print(c.getName() + " has nothing more to say")
                    self.characters.pop(i)
                    self.ready.append(c)
                    someone = True

            if(someone):
                return
            
            i += 1
