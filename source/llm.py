import re
import requests

class CMD:
    NOTHING = [ "NOTHING", ]
    PROPOSEEND = [ "PROPOSEEND", ]
    FORCEEND = [ "FORCEEND", ]

    SAY = [ "SAY", "message" ]
    SUMMARY = [ "SUMMARY", "summarized text" ]
    SCENARIO = [ "SCENARIO", "scenario description text" ]

    OBJECTIVE = [ "OBJECTIVE", "name", "description", "time at which it becomes invalid as HH:MM in 24-hour format" ]
class LLM:
    STORY_URL = "http://localhost:8081/v1/chat/completions"
    GAMEMASTER_URL = "http://localhost:8081/v1/chat/completions"
    SPEAKER_URL = "http://localhost:8081/v1/chat/completions"

    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"

    def __init__(self, url, logger=None):
        self._server_url = url
        self._memory = []
        self.logger = logger

    def __call(self, who, allowed, message, extra, failcount, reminder, save=True):
        buffer = ""

        # Extra Daten die nicht in memory sollen
        if(extra != None):
            buffer += extra + "\n"

        # Erlaubte Commands
        buffer += _formatCommandHint(allowed) + "\n"

        # memory
        temp = self._memory.copy()

        # Reminder wenn response failed
        if(reminder):
            buffer = "[REMINDER] " + reminder + "\n"

        self.__save(temp, LLM.SYSTEM, buffer)
        self.__save(temp, who, message)

        response = self.__send(temp)

        result, newReminder = _parseCommands(response, allowed)

        if not result:
            print("LLM FAILED #" + str(failcount))
            print("SAID:" + response + "\n" + "REMINDER:" + newReminder + "\n")
            return self.__call(who, allowed, message, extra, failcount + 1, newReminder, save)
        
        if save:
            self.__save(self._memory, who, message)
            self.__save(self._memory, LLM.ASSISTANT, response)

        return result
    
    def usercall(self, allowed, message="", extra=None, failcount=0, reminder=None):
        return self.__call(LLM.USER, allowed, message, extra, failcount, reminder)
    
    def syscall(self, allowed, message="", extra=None, failcount=0, reminder=None):
        return self.__call(LLM.SYSTEM, allowed, message, extra, failcount, reminder)

    def sysask(self, allowed, message="", extra=None, failcount=0, reminder=None):
        return self.__call(LLM.SYSTEM, allowed, message, extra, failcount, reminder, False)
    
    def syslisten(self, message):
        self.__save(self._memory, LLM.SYSTEM, message)
    
    def __save(self, mem, who, message):
        if len(mem) == 0:
            mem.append({"role": who, "content": message})
            return

        last = mem[-1]
        if last.get("role") == who:
            last["content"] += " " + message
        else:
            mem.append({"role": who, "content": message})


    #Send messages to llm an get response
    def __send(self, messages):
        response = requests.post(self._server_url, json={
                "messages": messages,
                "temperature": 0.7
        }, headers={"Content-Type": "application/json"})

        if not response.status_code == 200:
            print("Status Code Error: " + str(response.status_code))
            print(response.json())

        reply = response.json()["choices"][0]["message"]["content"].strip()

        clean_reply = reply.replace("\n", " ").replace("\r", "")

        if self.logger != None:
            self.logger.log(messages, clean_reply)

        return clean_reply

def _parseCommands(text, allowed):
    if not allowed or not isinstance(allowed[0], list):
        raise TypeError("Expected a list of allowed commands")

    # Liste erlaubter Kommandonamen
    command_names = [cmd[0] for cmd in allowed]

    # Regex zur Erkennung von Befehlen: #CMD(...) oder #CMD
    command_pattern = '|'.join(re.escape(cmd) for cmd in command_names)
    pattern = rf'#({command_pattern})(?:\{{([^#{{}}]*)\}})?'

    matches = list(re.finditer(pattern, text))
    if not matches:
        help_text = "; ".join(__formatCommand(elem) for elem in allowed)
        return None, "To answer use one of the following commands with correct syntax: " + help_text

    results = []
    for match in matches:
        command, param = match.groups()
        ans = {'command': command}

        # Parameter parsen, wenn vorhanden
        if param is not None:
            args = [p.strip() for p in param.split(';')] if param.strip() else []
            for i, arg in enumerate(args):
                ans[f'arg{i}'] = arg

        results.append(ans)

    # Validierung
    reminder = ""
    for cmd in results:
        reminder += __checkCommand(cmd, allowed)

    if reminder:
        return None, reminder

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
        joined_args = "; ".join(f"<{arg}>" for arg in args)
        return f"#{command_name}{{{joined_args}}}"

def __checkCommand(cmd: dict, allowed_cmds: list) -> str:
    if "command" not in cmd:
        return "Error: field 'command' is missing."

    name = cmd["command"]
    given_args = [v for k, v in sorted(cmd.items()) if k.startswith("arg")]

    # Suche erlaubten Befehl in erlaubten Kommandos
    matched = [entry for entry in allowed_cmds if entry[0] == name]
    if not matched:
        allowed_names = "; ".join(entry[0] for entry in allowed_cmds)
        return f"Unknown command '{name}'. Allowed are: {allowed_names}"

    # Erwartete Argumente vergleichen
    expected = matched[0][1:]
    print("expected: " + str(len(expected)) + " provided: " + str(len(given_args)))
    if len(given_args) != len(expected):
        correct_syntax = __formatCommand([name] + expected)
        return f"Wrong usage of #{name}. Expected syntax: {correct_syntax}"

    return ""

def _formatCommandHint(allowed_cmds: list) -> str:

    if not allowed_cmds:
        raise ValueError("Command list is empty")
    
    str = ""
    for elem in allowed_cmds:
        str += __formatCommand(elem) + "; "

    return "To answer use one of the following commands with correct syntax: " + str