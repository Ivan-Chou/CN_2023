import socket
import threading
import selectors
import sys
import json
import hashlib

from mylib import myHTTPmessage, myMutltithread

# ===============

# macro

MSGSIZE_MAX = 1024

MAXCONN = 512

SERVER_PORT = 51966 # 0xCAFE

# ===============

# global var

toShutDown = False

client_threads:list[threading.Thread] = [] # append client threads at here

lock_UserTable = threading.Lock()
UserTable = dict()

# ===============

# func

def client_conn(ClientSock: socket.socket, ClientAddr: str): #ClientInfo:tuple[socket.socket, str]

	myMutltithread.atomic_print(f"<INFO> New connection from: {ClientAddr}")

	# monitor input event by select
	sel = selectors.DefaultSelector()

	sel.register(ClientSock, selectors.EVENT_READ) # last param => default action (not used here)

	# log user info to global table ex. online

	while not toShutDown:
		httpMSG = myHTTPmessage.myHTTPmessage()

		if(len(sel.select(1)) > 0): # since only monitor 1 socket => (has something == can read)
			req_raw = ClientSock.recv(MSGSIZE_MAX)

			if(len(req_raw) == 0):
				# connection closed
				# jump out of loop and handle
				break

			req = myHTTPmessage.parseRequest(req_raw.decode(encoding="utf-8"))

			toPrint = "\n".join([
				"\n # ============================================== # \n",
				f"From {ClientAddr} received:\n",
				"\n".join([f"{key}: {req[key]}" for key in req]),
				"\n # ============================================== # \n"
			])

			myMutltithread.atomic_print(toPrint)

			# use PageHandler
			ClientSock.sendall(myHTTPmessage.PageHandlers.routing(route=req["target"])(req, httpMSG))
			
	
	# connection closed
	myMutltithread.atomic_print(f"<INFO> Connection from {ClientAddr} closed")

	sel.unregister(ClientSock)

	ClientSock.close()

	sel.close()

	return

def server_start(ServerAddr = "0.0.0.0"):
	ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	ServerSock.bind((ServerAddr, SERVER_PORT))

	myMutltithread.atomic_print(f"<INFO> Server start: start listening on port {SERVER_PORT}...")
	ServerSock.listen(MAXCONN)

	return ServerSock

def getCookieVal(ID:str, PW:str):
	return hashlib.sha256((ID + "|" + PW).encode()).hexdigest()

# ===============

# handlers

def index(request:dict[str, str], httpMSG:myHTTPmessage.myHTTPmessage):
	body = ""
	
	if(request["method"] == "GET"):
		with open("./webpage/html/index.html", mode="r", encoding="utf-8") as pageSrc:
			# thinking to read in as binary?
			body = pageSrc.read()

	elif(request["method"] == "POST"):
		post_val = myHTTPmessage.parseRequestBody(request["Content-Type"], request["body"])

		with lock_UserTable:
			if(post_val["act"] == "login"): # cookie name: Coffee
				myMutltithread.atomic_print("<INFO> Get into post login")

				if(post_val["ID"] in UserTable):
					cookie_val = getCookieVal(post_val["ID"], post_val["PW"])
					
					if ("Cookie" in request):
						clnt_cookies = myHTTPmessage.parseCookie(request["Cookie"])

						if ("Coffee" in clnt_cookies):
							cookie_val = clnt_cookies["Coffee"]

					myMutltithread.atomic_print(f"<INFO> cookie_val = {cookie_val}")
					
					if(cookie_val == UserTable[ post_val["ID"] ]["cookie"]):
						# login success
						# set cookie
						body = "login success :)"
						pass
						
						# redirect(not yet done)
						# with open("./webpage/html/index.html", mode="r", encoding="utf-8") as pageSrc:
						# 	# thinking to read in as binary?
						# 	body = pageSrc.read()
						# pass
					
					else:
						body = "Invalid ID & password :("
						
				else:
					body = f"No such user {post_val['ID']} :("

			elif(post_val["act"] == "reg"):
				# registration
				case = 0

				cookie_val = getCookieVal(post_val["ID"], post_val["PW"])

				if(post_val["ID"] in UserTable):
					case = 1
				else:
					# all ok => register
					UserTable[ post_val["ID"] ] = {
						"ID" : post_val["ID"],
						"cookie": cookie_val
						# don't save password, check hash to verify an user
					}

				body = json.dumps({"result" : str(case)})
			
			else:
				body=f"Invalid ID & password submit: {post_val['act']}"

	else:
		# error
		body = f"Invalid request method: {request['method']}"

	return httpMSG.response(status="200", body=body)
myHTTPmessage.PageHandlers.register("/", index)


def register():
	# sync. table
	pass
# myHTTPmessage.PageHandlers.register()

def login():
	# HTTP Set-Cookie header
	pass
# myHTTPmessage.PageHandlers.register()

def meeting():
	# Socket.io
	pass
# myHTTPmessage.PageHandlers.register()


# ===============

# main func

if __name__ == "__main__": # main func
	ServerSock = server_start()

	# check if handlers are correct
	myHTTPmessage.PageHandlers.listHandlers()

	# main thread should handle STDIN (for admin command) and server socket(accept new connections)
	sel = selectors.DefaultSelector()

	sel_keys = dict()
	sel_keys["ServerSock"] = sel.register(ServerSock, selectors.EVENT_READ)
	sel_keys["stdin"] = sel.register(sys.stdin, selectors.EVENT_READ)

	while not toShutDown:
		sel_events = sel.select(1)

		if(len(sel_events) > 0): # something to read
			ready_stat = dict([(sel_keys[name], False) for name in sel_keys])

			for (key, events) in sel_events:
				ready_stat[key] = True

			if(ready_stat[ sel_keys["ServerSock"] ]):
				# a new connection
				clnt = threading.Thread(target=client_conn, args=ServerSock.accept())
				
				clnt.start()
				
				client_threads.append(clnt)

			if(ready_stat[ sel_keys["stdin"] ]):
				cmd = input()
				
				if(cmd == "stop"):
					myMutltithread.atomic_print("<INFO> Server is going to shut down...")
					toShutDown = True
				elif(cmd == "showuser"):
					with lock_UserTable:
						myMutltithread.atomic_print("\n".join([
							"\n # ============================================== # \n",
							"<INFO> Showing User Table:\n",
							"\n".join([f"{usr}: {UserTable[usr]}" for usr in UserTable]),
							"\n # ============================================== # \n"
						]))
				else:
					myMutltithread.atomic_print(f"<ERR> Unknown command : {cmd}")

		# join dead thread
		for conn in client_threads:
			if not conn.is_alive():
				conn.join()

				client_threads.remove(conn)

	# myMutltithread.atomic_print("<INFO> Server shutting down...")

	for conn in client_threads:
		conn.join()

	# myMutltithread.atomic_print("<INFO> Threads all joined")

	ServerSock.close()

	sel.unregister(ServerSock)

	sel.close()

	myMutltithread.atomic_print("<INFO> Server shutted down.")

# main:

# toShutDown = true

# selector