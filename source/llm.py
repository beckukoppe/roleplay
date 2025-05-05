import re
import requests

ASSISTANT = "assistant"
USER = "user"
SYSTEM = "system"
class LLM:
    STORY_URL = "http://localhost:8081/v1/chat/completions"
    GAMEMASTER_URL = "http://localhost:8081/v1/chat/completions"
    SPEAKER_URL = "http://localhost:8081/v1/chat/completions"

    STORY_COMMANDS = ["TIME", "NAME", "CHARACTER", "STORY", "GAMEMASTER"]
    GAMEMASTER_COMMANDS = ["NOTHING", "SCENARIO", "SUMMARY", "OBJECTIVE"]
    SPEAKER_COMMANDS=["NOTHING", "SAY", "FORCEEND", "PROPOSEEND", "SUMMARY"]

    def __init__(self, server_url, initial_prompt, commands):
        self._server_url = server_url
        self._memory = []
        self._system(initial_prompt)
        self._commands = commands

    def call(self, message, context=None, failcount=0, reminder=None):
        temp = self._memory.copy()

        if(context):
            temp.append({"role": SYSTEM, "content": "context:" + context})
        temp.append({"role": USER, "content": "request:" + message})
        if(reminder):
            temp.append({"role": SYSTEM, "content": "REMINDER:" + reminder})
        response = self._send(temp)
        result, newReminder = _parseCommands(response, self._commands)

        if(result):
            self._user(message)
            self._llm(response)
            return result
        else:
            print("LLM FAILED TO FOLLOW ORDERS: #" + str(failcount))
            print(response + "\n")
            return self.call(message, context, failcount + 1, newReminder)

    
    def ask(self, message, context=None, failcount=0, reminder=None):
        temp = self._memory.copy()
        if(context):
            temp.append({"role": SYSTEM, "content": "context:" + context})
        temp.append({"role": USER, "content": "request:" + message})
        if(reminder):
            temp.append({"role": SYSTEM, "content": "REMINDER:" + reminder})     
        response = self._send(temp)
        
        result, newReminder = _parseCommands(response, self._commands)

        if(result):
            return result
        else:
            print("LLM FAILED TO FOLLOW ORDERS: #" + str(failcount))
            print(response + "\n")
            return self.ask(message, context, failcount + 1, newReminder)
    
    def listen(self, message):
        self._user(message)
    
    def briefing(self, info):
        self._system(info)

    def memorize(self, conversation):
        response = self.ask("#SUMMARIZE(include what you feel and think about it and what you may would do at the next occasion){" + conversation + "}")
        assert len(response) > 0, "LLM ERROR"
        for cmd in response:
            self._system("#SUMMARY(of a conversation you took place in){" + cmd.get("data", "") + "}")

    def sumup(self, conversation):
        response = self.ask("#SUMMARIZE{" + conversation + "}. Answer with #SUMMARY{content}")
        assert len(response) > 0, "LLM ERROR"
        for cmd in response:
            self._system("#SUMMARY(of a conversation you took place in){" + cmd.get("data", "") + "}")

    def _send(self, messages):
        response = requests.post(self._server_url, json={
                #"model": MODEL_NAME,
                "messages": messages,
                "temperature": 0.7
        }, headers={"Content-Type": "application/json"})

        if not response.status_code == 200:
            print("Status Code Error: " + str(response.status_code))
            print(response.json())

        reply = response.json()["choices"][0]["message"]["content"].strip()

        clean_reply = reply.replace("\n", " ").replace("\r", "")
        return clean_reply
        
    def _llm(self, content):
        self._memory.append({"role": ASSISTANT, "content": content})

    def _user(self, content):
        self._memory.append({"role": USER, "content": content})

    def _system(self, content):
        self._memory.append({"role": SYSTEM, "content": content})

def _parseCommands(text, commands):
    """
    Parse commands of the form:
    - #COMMAND{data}
    - #COMMAND
    - #COMMAND(param)least
    Returns:
        tuple: (success: bool, results: list of dict)
    """

    # Erlaubte Kommandos absichern
    command_pattern = '|'.join(re.escape(cmd) for cmd in commands)
    
    # Regex: fängt COMMAND, optional {data} oder (param)
    pattern = rf'#({command_pattern})(?:\{{([^}}]*)\}}|\(([^)]*)\))?'

    matches = list(re.finditer(pattern, text))

    if not matches:
        return [], "use one of the specified commands with correct syntax!"

    results = []
    for match in matches:
        command, data, param = match.groups()
        ans = {'command': command}
        
        if data is not None:
            ans['data'] = data
        elif param is not None:
            ans['param'] = param
        
        results.append(ans)

    reminder = ""
    for cmd in results:
        reminder += _checkCommand(cmd)

    if(reminder != ""):
        results = None

    if(results == None):
        reminder = "You must use one of the specified commands with correct syntax!"
    
    return results, reminder

def _checkCommand(command):
    #if(command.get("command") == "NOTHING"):
    
    if(command.get("command") == "SAY"):
        if(command.get("data", "") == ""):
            return "Syntax of #SAY is '#SAY{...}' where ... must be what you want to say"

    if(command.get("command") == "OBJECTIVE"):
        if (command.get("data") == "") or (command.get("param" == "")):
            return "Syntax of #OBJECTIVE is '#OBJECTIVE(time){description}'"

    #if(command.get("command") == "PROPOSEEND"):

    #if(command.get("command") == "SUMMARY"):
        #return ""

    if(command.get("command") == "SCENARIO"):
        if(command.get("data", "") == ""):
            return "use correct syntax for #SCENARIO!"

    return ""



















    nothing = [ "#NOTHING", "use when you dont want ..."]
    say = []
    kill = []

    llm.call(propt, [nothing, say, kill])