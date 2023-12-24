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

COOKIE_NAME = "Coffee"

# ===============

# global var

toShutDown = False

client_threads:list[threading.Thread] = [] # append client threads at here

lock_RegisterTable = threading.Lock()
RegisterTable:dict[str, dict[str, str]] = dict() # dict[username, dict[info, value]]

lock_OnlineTable = threading.Lock()
OnlineTable:dict[str, str] = dict() # dict[username, call_addr]

# ===============

# func

def client_conn(ClientSock: socket.socket, ClientAddr: str): #ClientInfo:tuple[socket.socket, str]

	myMutltithread.atomic_print(f"<INFO> New connection from: {ClientAddr}")

	# monitor input event by select
	sel = selectors.DefaultSelector()

	sel.register(ClientSock, selectors.EVENT_READ) # last param => default action (not used here)

	# log user info to global table ex. online

	while not toShutDown:
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
			ClientSock.sendall(myHTTPmessage.PageHandlers.routing(route=req["target"])(req))
			
	
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

def getCookieHash(ID:str, PW:str):
	return hashlib.sha256((ID + "|" + PW).encode()).hexdigest()

def getUserIDFromCookie(cookie_val:str):
	return cookie_val.split("-")[0]

def getUserHashFromCookie(cookie_val:str):
	return cookie_val.split("-")[1]

def verifyUserByCookie(cookie_val:str):
	"""
	cookie form: (user id) + "-" + (hash)
	"""

	(userID, hash) = cookie_val.split("-")

	return ((userID in RegisterTable) and (RegisterTable[userID]["hash"] == hash))

# ===============

# handlers

def index(request:dict[str, str]):
	httpMSG = myHTTPmessage.myHTTPmessage()
	
	body = ""
	
	if(request["method"] == "GET"):
		with open("./webpage/html/index.html", mode="r", encoding="utf-8") as pageSrc:
			body = pageSrc.read()

	elif(request["method"] == "POST"):

		post_val = myHTTPmessage.parseRequestBody(request["Content-Type"], request["body"])

		with lock_RegisterTable:
			if(post_val["act"] == "login"): # cookie name: Coffee
				myMutltithread.atomic_print("<INFO> Get into post login")

				if(post_val["ID"] in RegisterTable):
					cookie_hash = getCookieHash(post_val["ID"], post_val["PW"])
					
					if ("Cookie" in request):
						clnt_cookies = myHTTPmessage.parseCookie(request["Cookie"])

						if (COOKIE_NAME in clnt_cookies):
							cookie_hash = clnt_cookies[COOKIE_NAME].split("-")[1]

					myMutltithread.atomic_print(f"<INFO> cookie_hash = {cookie_hash}")
					
					if(cookie_hash == RegisterTable[ post_val["ID"] ]["hash"]):
						# login success
						
						# set cookie, redirection
						httpMSG.setStatus("303")

						httpMSG.setHeader({
							"Location" : "/loggedin",
							"Set-Cookie" : f"{COOKIE_NAME}={post_val['ID']}-{cookie_hash}; Expires={myHTTPmessage.HTTPdate(later=3600)}"
						})
					
					else:
						body = "Invalid ID & password :("
						
				else:
					body = f"No such user {post_val['ID']} :("

			elif(post_val["act"] == "reg"):
				# registration
				case = 0

				cookie_hash = getCookieHash(post_val["ID"], post_val["PW"])

				if(post_val["ID"] in RegisterTable):
					case = 1
				else:
					# all ok => register
					RegisterTable[ post_val["ID"] ] = {
						"ID" : post_val["ID"],
						"hash": cookie_hash
						# don't save password, check hash to verify an user
					}

				body = json.dumps({"result" : str(case)})

				httpMSG.setContentType("application/json")
			
			else:
				body=f"Invalid ID & password submit: {post_val['act']}"

	else:
		# error
		body = f"Invalid request method: {request['method']}"

	return httpMSG.response(body=body)
myHTTPmessage.PageHandlers.register("/", index)

def loggedin(request:dict[str, str]):
	httpMSG = myHTTPmessage.myHTTPmessage()

	body = ""

	if("Cookie" not in request):
		httpMSG.setStatus("403")

		body = "You have to log in to access the page"

		return httpMSG.response(body=body)
	
	cookies = myHTTPmessage.parseCookie(request["Cookie"])

	if(f"{COOKIE_NAME}" not in cookies) or (not verifyUserByCookie(cookies[COOKIE_NAME])):
		httpMSG.setStatus("403")

		body = "Invalid or unexisted login cookie for CAFE"

		return httpMSG.response(body=body)

	# => valid user => log in table update
	userID = getUserIDFromCookie(cookies[COOKIE_NAME])

	with lock_OnlineTable:
		if(userID not in OnlineTable):
			OnlineTable[userID] = "" # temporary not know connection

	if(request["method"] == "GET"):
		with open("./webpage/html/loggedin.html", mode="r", encoding="utf-8") as file:
			body = file.read()

	elif(request["method"] == "POST"):
		post_val = myHTTPmessage.parseRequestBody(request["Content-Type"], request["body"])

		if(post_val["act"] == "logout"):
			# clear from OnlineTable
			with lock_OnlineTable:
				OnlineTable.pop(userID)
			
			# redirect to "/"
			httpMSG.setStatus("303")
			
			httpMSG.setHeader({
				"Location": "/"
			})
	else:
		body = f"Invalid request method: {request['method']}"
	
	return httpMSG.response(body=body)
myHTTPmessage.PageHandlers.register("/loggedin", loggedin)

def meeting():
	# Socket.io
	pass
# myHTTPmessage.PageHandlers.register()


# ===============

# main func

if __name__ == "__main__": # main func
	ServerSock = server_start()

	myMutltithread.atomic_print("\n".join([
		"\n # ============================================== # \n",
		"<DEBUG> DefaultFileUtil:",
		"\n".join(f"{key}: header = {myHTTPmessage.DefaultFileUtil[key]['response'].header}" for key in myHTTPmessage.DefaultFileUtil),
		"\n # ============================================== # \n"
	]))

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
				elif(cmd == "showreg"):
					with lock_RegisterTable:
						myMutltithread.atomic_print("\n".join([
							"\n # ============================================== # \n",
							"<INFO> Showing Registration Table:\n",
							"\n".join([f"{usr}: {RegisterTable[usr]}" for usr in RegisterTable]),
							"\n # ============================================== # \n"
						]))
				elif(cmd == "showonline"):
					with lock_RegisterTable:
						myMutltithread.atomic_print("\n".join([
							"\n # ============================================== # \n",
							"<INFO> Showing Online User Table:\n",
							"\n".join([f"{usr}: {OnlineTable[usr]}" for usr in OnlineTable]),
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