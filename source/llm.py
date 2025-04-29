import re
import requests

class LLM:
    STORY_URL = "http://localhost:8081/v1/chat/completions"
    GAMEMASTER_URL = "http://localhost:8081/v1/chat/completions"
    SPEAKER_URL = "http://localhost:8081/v1/chat/completions"

    STORY_COMMANDS = ["TIME", "NAME", "CHARACTER", "STORY", "GAMEMASTER"]
    GAMEMASTER_COMMANDS = ["SCENARIO", "SUMMARY"]
    SPEAKER_COMMANDS=["NOTHING", "SAY", "FORCEEND", "PROPOSEEND", "SUMMARY"]

    def __init__(self, server_url, initial_prompt, commands):
        self._server_url = server_url
        self._memory = []
        self._system(initial_prompt)
        self._commands = commands

    def call(self, message, context=None, failcount=0):
        temp = self._memory.copy()

        if(context):
            temp.append({"role": "user", "content": "conversation:" + context})
        temp.append({"role": "user", "content": "request:" + message}) 
        response = self._send(temp)
        result = _parseCommands(response, self._commands)

        if(result):
            self._user(message)
            self._llm(response)
            return result
        else:
            print("LLM FAILED TO FOLLOW ORDERS: #" + str(failcount))
            print(response + "\n")
            return self.call(message, context, failcount + 1)

    
    def ask(self, message, context=None, failcount=0):
        temp = self._memory.copy()
        if(context):
            temp.append({"role": "user", "content": "conversation:" + context})
        temp.append({"role": "user", "content": "request:" + message})   
        response = self._send(temp)
        result = _parseCommands(response, self._commands)

        if(result):
            return result
        else:
            print("LLM FAILED TO FOLLOW ORDERS: #" + str(failcount))
            print(response + "\n")
            return self.ask(message, context, failcount + 1)
    
    def listen(self, message):
        self._user(message)
    
    def briefing(self, info):
        self._system(info)

    def memorize(self, conversation):
        response = self.ask("#SUMMARIZE(include what you feel and think about it and what you may would do if meeting again){" + conversation + "}")
        assert len(response) > 0, "LLM ERROR"
        for cmd in response:
            self._system("#SUMMARY(of a conversation you took place in){" + cmd.get("data", "") + "}")

    def sumup(self, conversation):
        response = self.ask("#SUMMARIZE{" + conversation + "}. Answer with #SUMMARY{content}")
        assert len(response) > 0, "LLM ERROR"
        for cmd in response:
            print(cmd)
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
        self._memory.append({"role": "system", "content": content})

    def _user(self, content):
        self._memory.append({"role": "user", "content": content})

    def _system(self, content):
        self._memory.append({"role": "user", "content": content})

def _parseCommands(text, commands):
    """
    Parse commands of the form:
    - #COMMAND{data}
    - #COMMAND
    - #COMMAND(param)
    
    Args:
        text (str): The input text containing commands.
        commands (list of str): List of allowed command names.

    Returns:
        tuple: (success: bool, results: list of dict)
    """

    # Erlaubte Kommandos absichern
    command_pattern = '|'.join(re.escape(cmd) for cmd in commands)
    
    # Regex: fängt COMMAND, optional {data} oder (param)
    pattern = rf'#({command_pattern})(?:\{{([^}}]*)\}}|\(([^)]*)\))?'

    matches = list(re.finditer(pattern, text))

    if not matches:
        return []

    results = []
    for match in matches:
        command, data, param = match.groups()
        result = {'command': command}
        
        if data is not None:
            result['data'] = data
        elif param is not None:
            result['param'] = param
        
        results.append(result)
    
    return results



