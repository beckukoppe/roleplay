from llm import CMD
import util

class Operation:
    DECIDE = [
        "DECIDE",
        "question_text",      # Die Entscheidungsfrage, z. B. "Sollen wir stürmen oder weiter verhandeln?"
        "option_a/option_b/..."    # Liste von Optionen als Strings, z. B. ["Stürmen", "Warten", "Verhandeln"]
    ]

    END = ["END"]  # Signalisiert das natürliche oder erzwungene Ende der Operation

    # Optional – für Realismussteigerung, könnte implementiert werden
    REPORT = ["REPORT", "message"]

    def __init__(self, description, agent, gamemaster):
        self.description = description  # z.B. "Special Ops-Team befreit Geiseln"
        self.agent = agent              # z.B. ein Team oder Kollege (Objekt mit Name)
        self.gamemaster = gamemaster    # LLM-gesteuerte Entscheidungsinstanz
        self.transcript = ""
        self.ended = False
        self.step_count = 0

    def log(self, text):
        self.transcript += text + "\n"
        print("[PROTOKOLL] " + text)

    def report(self, message):
        self.transcript += "#REPORT(" + message + ")\n"
        print("#REPORT(" + message + ")")

    def start(self):
        self.report(f"Operation started: {self.description} with {self.agent}")
        intro = self.gamemaster.call([["INTRO", "description"],], "Profide an intro for the following operation:" + self.description + "agent: " + self.agent + ". This operation will be played step by step afterwards")
        self.log(intro[0].get("arg0"))

        while not self.ended:
            self.step()

        self.log("Operation ended.")
        self.gamemaster.summarize(self.transcript)

    def step(self):
        self.step_count += 1

        # Spielt ein Segment der Operation ab
        answer = self.gamemaster.call([Operation.REPORT, Operation.END], "tell one step in the operation or end it")
        if answer[0].get("command") == "END":
                self.report("Operation has been finished.")
                self.ended = True
                return
        #print(answ)
        situation_report = answer[0].get("arg0")
        self.log(situation_report)

        # Jetzt kommt eine Entscheidungssituation

        if(self.step_count < 5):
            cmds = self.gamemaster.ask(
            [   Operation.DECIDE, Operation.END],
                "#DECIDE - Decision point reached. Provide options or end operation. Seperate question and options with ;.  Seperate options with /. Dont include the options in the question but provide them extra!"
            )
        elif (self.step_count < 15):
            cmds = self.gamemaster.ask(
            [   Operation.DECIDE, Operation.END],
                "#DECIDE - Decision point reached. Slowly but surely navigate towards an end of operation! Provide options or end operation. Seperate question and options with ;.  Seperate options with /. Dont include the options in the question but provide them extra!"
            )
        else:
            cmds = self.gamemaster.ask(
            [   Operation.DECIDE, Operation.END],
                "#DECIDE - Decision point reached. Provide one last decision and end operation. Seperate question and options with ;.  Seperate options with /. Dont include the options in the question but provide them extra! at the end include #END as second command!"
            )

        assert len(cmds) > 0, "LLM ERROR"

        for cmd in cmds:
            print(cmd)
            if cmd.get("command") == "DECIDE":
                question = cmd.get("arg0")
                options_str = cmd.get("arg1")
                options = options_str.split("/")  # ← Hier erfolgt die Trennung

                self.log(f"{self.agent} fragt: {question}")
                for idx, opt in enumerate(options):
                    print(f"{idx}. {opt}")

                choice = self.getPlayerChoice(len(options))
                selected = options[choice]
                self.log(f"SPIELER wählt: {selected}")

                self.gamemaster.listen(question + " - " + selected)

                return

            elif cmd.get("command") == "NOTHING":
                return  # Routinefortgang

            elif cmd.get("command") == "END":
                self.report("Operation has been finished.")
                self.ended = True
                return

    def getPlayerChoice(self, num_options):
        while True:
            try:
                choice = int(input("Deine Entscheidung: "))
                if 0 <= choice < num_options:
                    return choice
            except ValueError:
                pass
            print("Ungültige Eingabe, bitte erneut versuchen.")