from llm import CMD
import util

class Operation:
    DECIDE = [
        "DECIDE",
        "text",      # Die Entscheidungsfrage, z. B. "Sollen wir stürmen oder weiter verhandeln?"
        "options"    # Liste von Optionen als Strings, z. B. ["Stürmen", "Warten", "Verhandeln"]
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

    def log(self, text):
        self.transcript += text + "\n"
        print("[PROTOKOLL] " + text)

    def report(self, message):
        self.transcript += "#REPORT(" + message + ")\n"
        print("#REPORT(" + message + ")")

    def start(self):
        self.report(f"Operation gestartet: {self.description} durch {self.agent.getName()}")
        intro = self.gamemaster.getScenario("operation", self.agent.getName() + ": " + self.description)
        self.log(intro)

        while not self.ended:
            self.step()

        self.log("Operation abgeschlossen.")
        self.gamemaster.summarize(self.transcript)

    def step(self):
        # Spielt ein Segment der Operation ab
        situation_report = self.gamemaster.askNarration(self.description, self.transcript)
        self.log(situation_report)

        # Jetzt kommt eine Entscheidungssituation
        cmds = self.gamemaster.ask(
            [Operation.DECIDE, CMD.NOTHING, Operation.END],
            "#DECIDE - Decision point reached. Provide options or end operation."
        )

        assert len(cmds) > 0, "LLM ERROR"

        for cmd in cmds:
            if cmd.get("command") == "DECIDE":
                options = cmd.get("options")
                question = cmd.get("text")

                self.log(f"{self.agent.getName()} fragt: {question}")
                for idx, opt in enumerate(options):
                    print(f"{idx}. {opt}")

                choice = self.getPlayerChoice(len(options))
                selected = options[choice]
                self.log(f"SPIELER wählt: {selected}")

                self.gamemaster.processPlayerDecision(self.description, selected)
                return

            elif cmd.get("command") == "NOTHING":
                return  # Routinefortgang

            elif cmd.get("command") == "END":
                self.report("Operation wurde abgeschlossen.")
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