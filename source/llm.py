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
        self._history = []
        self._system(initial_prompt)
        self._commands = commands

    def call(self, message):
        self._user(message)
        response = self._send(self._history)
        self._system(response)
        print(response)

        return _parseCommands(response, self._commands)
    
    def listen(self, message):
        self._user(message)

    def getSummary(self):
        return self.call("#SUMARIZE")
    
    def briefing(self, info):
        self._system("briefing:" + info)

    def _send(self, messages):
        try:
            response = requests.post(self._server_url, json={
                "messages": self._history,
                "temperature": 0.7
            }, headers={"Content-Type": "application/json"})

            reply = response.json()["choices"][0]["message"]["content"].strip()

            clean_reply = reply.replace("\n", " ").replace("\r", "")
            return clean_reply
            
        except Exception as e:
            print(f"An LLM-Server Error occured: {e}")
            return None
        
    def _system(self, content):
        self._history.append({"role": "system", "content": content})

    def _user(self, content):
        self._history.append({"role": "user", "content": content})


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



