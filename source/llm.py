import re
import requests

ASSISTANT = "assistant"
USER = "user"
SYSTEM = "system"

class CMD:
    NOTHING = [ "NOTHING", ]
    PROPOSEEND = [ "PROPOSEEND", ]
    FORCEEND = [ "FORCEEND", ]

    SAY = [ "SAY", "message" ]
    SUMMARY = [ "SUMMARY", "summarized text" ]
    SCENARIO = [ "SCENARIO", "scenario description text" ]

    OBJECTIVE = [ "OBJECTIVE", "name", "description", "time at which it becomes invalid" ]
class LLM:
    STORY_URL = "http://localhost:8081/v1/chat/completions"
    GAMEMASTER_URL = "http://localhost:8081/v1/chat/completions"
    SPEAKER_URL = "http://localhost:8081/v1/chat/completions"

    def __init__(self, server_url, initial_prompt, logger=None):
        self._server_url = server_url
        self._memory = []
        self.syslisten(initial_prompt)
        self.logger = logger

    def __call(self, who, allowed, message, extra, failcount, reminder):
        temp = self._memory.copy()

        if(extra != None):
            temp.append({"role": "system", "content": extra})

        temp.append({"role": "system", "content": _formatCommandHint(allowed)})

        temp.append({"role": who, "content": message})
        self._memory.append({"role": who, "content": message})

        if(reminder):
            temp.append({"role": SYSTEM, "content": "[REMINDER]" + reminder})

        response = self.__send(temp)
        result, newReminder = _parseCommands(response, allowed)

        if(result):
            self._memory.append({"role": "assistant", "content": response})

            if self.logger != None:
                self.logger.log_call(self._memory)
            return result
        else:
            print("LLM FAILED #" + str(failcount))
            print("SAID:" + response + "\n" + "REMINDER:" + newReminder + "\n")
            return self.__call(who, allowed, message, extra, failcount + 1, newReminder)
        
    def usercall(self, allowed, message="", extra=None, failcount=0, reminder=None):
        return self.__call("user", allowed, message, extra, failcount, reminder)
    
    def syscall(self, allowed, message="", extra=None, failcount=0, reminder=None):
        return self.__call("system", allowed, message, extra, failcount, reminder)

    def sysask(self, allowed, message="", extra=None, failcount=0, reminder=None):
        temp = self._memory.copy()

        if(extra):
            temp.append({"role": "system", "content": extra})

        temp.append({"role": "system", "content": _formatCommandHint(allowed)})

        temp.append({"role": "system", "content": message})

        if(reminder):
            temp.append({"role": SYSTEM, "content": "[REMINDER]" + reminder})

        response = self.__send(temp)
        result, newReminder = _parseCommands(response, allowed)

        if(result):
            if self.logger != None:
                self.logger.log_call(self._memory, response)
            return result
        else:
            print("LLM FAILED #" + str(failcount))
            print("SAID:" + response + "\n" + "REMINDER:" + newReminder + "\n")
            return self.sysask(allowed, message, extra, failcount + 1, newReminder)
    
    def __listen(self, who, message):
        self._memory.append({"role": who, "content": message})

    def userlisten(self, message):
        self.__listen("user", message)

    def syslisten(self, message):
        self.__listen("system", message)

    def __send(self, messages):
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

def _parseCommands(text, allowed):
    if not allowed or not isinstance(allowed[0], list):
        raise TypeError(f"Expected a list for allowed command")

    # Erlaubte Kommandonamen extrahieren
    command_names = [cmd[0] for cmd in allowed]

    # Regex pattern bilden
    command_pattern = '|'.join(re.escape(cmd) for cmd in command_names)
    pattern = rf'#({command_pattern})(?:\(([^)]*)\))?'

    matches = list(re.finditer(pattern, text))
    if not matches:
        str = ""
        for elem in allowed:
            str += __formatCommand(elem) + ", "

        return None,"To answer use one of the following commands with correct syntax: " + str

    results = []
    for match in matches:
        command, param = match.groups()
        ans = {'command': command}

        if param is not None:
            args = [p.strip() for p in param.split(';')] if param.strip() else []
            for i, arg in enumerate(args):
                ans[f'arg{i}'] = arg

        results.append(ans)

    # Fehlerprüfung
    reminder = ""
    for cmd in results:
        reminder += __checkCommand(cmd, allowed)

    return results, ""


def __formatCommand(cmd: list) -> str:
    if not cmd:
        raise ValueError("Command list is empty")

    command_name = cmd[0]
    args = cmd[1:]

    if not isinstance(command_name, str):
        raise TypeError("Command name must be a string")

    if not args:
        return f"#{command_name}"
    else:
        joined_args = ", ".join(f"<{arg}>" for arg in args)
        return f"#{command_name}({joined_args})"

def __checkCommand(cmd: dict, allowed_cmds: list) -> str:
    if "command" not in cmd:
        return "Error: field 'command' is missing."

    name = cmd["command"]
    given_args = [v for k, v in sorted(cmd.items()) if k.startswith("arg")]

    # Suche erlaubten Befehl in erlaubten Kommandos
    matched = [entry for entry in allowed_cmds if entry[0] == name]
    if not matched:
        allowed_names = ", ".join(entry[0] for entry in allowed_cmds)
        return f"Unknown command '{name}'. Allowed are: {allowed_names}"

    # Erwartete Argumente vergleichen
    expected = matched[0][1:]
    if len(given_args) != len(expected):
        correct_syntax = __formatCommand([name] + expected)
        return f"Wrong usage of #{name}. Expected syntax: {correct_syntax}"

    return ""

def _formatCommandHint(allowed_cmds: list) -> str:

    if not allowed_cmds:
        raise ValueError("Command list is empty")
    
    str = ""
    for elem in allowed_cmds:
        str += __formatCommand(elem) + ", "

    return "To answer use one of the following commands with correct syntax: " + str
