import re
import requests

class LLM:
    STORY_URL = "http://localhost:8081/v1/chat/completions"
    GAMEMASTER_URL = "http://localhost:8081/v1/chat/completions"
    SPEAKER_URL = "http://localhost:8081/v1/chat/completions"

    STORY_COMMANDS = ["TIME", "NAME", "CHARACTER"]
    GAMEMASTER_COMMANDS = ["NOTHING", "STARTPROPMPT"]
    SPEAKER_COMMANDS=["NOTHING", "SAY", "FORCEEND", "PROPOSEEND"]

    def __init__(self, server_url, initial_prompt, commands):
        self._server_url = server_url
        self._memory = []
        self._system(initial_prompt)
        self._commands = commands

    def call(self, message):
        self._user(message)
        response = self._send("memory:{" + self._stringFromMemory() + "} request:{" + message + "}")
        self._llm(response)

        return _parseCommands(response, self._commands)
    
    def ask(self, message):
        self._user(message)
        response = self._send("memory:{" + self._stringFromMemory() + "request:{" + "}")

        return _parseCommands(response, self._commands)
    
    def listen(self, message):
        self._user(message)
    
    def briefing(self, info):
        self._system(info)

    def memorize(self, conversation):
        response = self.ask("#SUMMARIZE(include what you feel and think about it and what you may would do if meeting again){" + conversation + "}")
        self._system("#SUMMRAY(of a conversation you took place in){" + response + "}")

        return _parseCommands(response, self._commands)

    def _send(self, messages):
        try:
            response = requests.post(self._server_url, json={
                #"model": MODEL_NAME,
                "messages": self._memory,
                "temperature": 0.7
            }, headers={"Content-Type": "application/json"})


            if not response.status_code == 200:
                print("Status Code Error: " + response.status_code)
                print(response)

            reply = response.json()["choices"][0]["message"]["content"].strip()

            clean_reply = reply.replace("\n", " ").replace("\r", "")
            return clean_reply
            
        except Exception as e:
            print(f"LLM-Server-Error: {e}")
            return None
        
    def _llm(self, content):
        self._memory.append({"role": "llm", "content": content})

    def _user(self, content):
        self._memory.append({"role": "user", "content": content})

    def _system(self, content):
        self._memory.append({"role": "system", "content": content})

    def _stringFromMemory(self):
        """Format the memory as a readable string."""
        if not self._memory:
            return ""

        lines = []
        for entry in self._memory:
            role = entry.get("role", "unknown")
            content = entry.get("content", "")
            lines.append(f"{role}: {content}")

        return "".join(lines)


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



