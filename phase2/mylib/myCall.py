import json
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room

from mylib.myMutltithread import atomic_print
from mylib import myUserData

CALLPORT = 51968 # 0xCAFE + 2

app = Flask(__name__)
callManager = SocketIO(app=app, cors_allowed_origins="*")

# OnlineTable: OnlineTable[userID] ---> the "roomID" user is at
# SIDTable: SIDTable[sid] ---> the "userID" which the sid is associated to

@callManager.on("connect")
def new_conn_handle(data):
    sid = request.sid

    atomic_print(f"<INFO> CallServer: socket.io connected, sid = {sid}")


@callManager.on("join_room")
def join_room_handle(data:str=""):
    sid = request.sid
    
    # client should emit with a json string
    atomic_print("<INFO> user transfers: " + data)
    
    if(not data):
        return

    data = json.loads(data)

    roomID = data["roomID"] # roomID => random / cookie?
    userID = data["userID"]

    with myUserData.lock_SIDTable:
        myUserData.SIDTable[sid] = userID

    with myUserData.lock_OnlineTable:
        myUserData.OnlineTable[userID] = roomID

    join_room(room=roomID, sid=sid) # socket.join(roomid)

    emit("user_connected", userID, to=roomID, skip_sid=[sid]) # socket.to(roomId).broadcast.emit('user-connected', userId)

@callManager.on("ready")
def transferReady(data:str):
    sid = request.sid
    
    data = json.loads(data)

    atomic_print(f"<DEBUG> CallServer: received ready, {data}")

    emit("receiver_ready", {"sender": data["sender"], "receiver": data["receiver"]}, to=data["roomID"], skip_sid=sid)

@callManager.on("disconnect")
def disconnect_handle():
    sid = request.sid

    userID = ""
    roomID = ""

    with myUserData.lock_SIDTable:
        userID = myUserData.SIDTable[sid]

        myUserData.SIDTable.pop(sid)

    with myUserData.lock_OnlineTable:
        roomID = myUserData.OnlineTable[userID]
        
        myUserData.OnlineTable.pop(userID)

    emit("user_disconnected", userID, to=roomID, skip_sid=[sid])

# ==============================================================

# cam on & off 

@callManager.on("cam_off")
def cam_off(data:str=""):
    # should have string: {userID, roomID}
    sid = request.sid

    data = json.loads(data)

    userID = data["userID"]
    roomID = data["roomID"]

    # others should close that person's camera
    emit("other_cam_off", userID, to=roomID, skip_sid=[sid])

@callManager.on("cam_on")
def cam_on(data:str):
    sid = request.sid

    data = json.loads(data)

    userID = data["userID"]
    roomID = data["roomID"]

    # others should close that person's camera
    emit("other_cam_on", userID, to=roomID, skip_sid=[sid])

# ==============================================================

def callStartup():
    atomic_print(f"<INFO> CallServer starting...")

    callManager.run(app=app, host="0.0.0.0", port=CALLPORT)

    atomic_print(f"<ERR> CallServer terminated")