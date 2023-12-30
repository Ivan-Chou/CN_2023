import threading

lock_RegisterTable = threading.Lock()
RegisterTable:dict[str, dict[str, str]] = dict() # dict[username, dict[info, value]]

lock_OnlineTable = threading.Lock()
OnlineTable:dict[str, str] = dict() # dict[username, roomID]

lock_PostTable = threading.Lock()
PostTable:list[dict[str, str]] = []

lock_SIDTable = threading.Lock()
SIDTable:dict[str, str] = dict()