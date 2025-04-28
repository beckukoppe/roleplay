def readFile(str):
    o = ""
    with open(str, "r", encoding="utf-8") as f:
        o = f.read().strip()
    return o