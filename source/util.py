def readFile(str):
    o = ""
    with open(str, "r", encoding="utf-8") as f:
        o = f.read().strip()
    return o

def try_remove(list, item):
    try:
        list.remove(item)
    except ValueError:
        pass 
