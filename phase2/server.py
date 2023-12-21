import socket
import threading
import selectors
import sys

from mylib import myHTTPmessage

# ===============

# macro

MSGSIZE_MAX = 1024

MAXCONN = 512

SERVER_PORT = 51966 # 0xCAFE

# ===============

# global var

toShutDown = False

client_threads = [] # append client threads at here

# ===============

# handlers

def index(request, httpMSG:myHTTPmessage.myHTTPmessage):
	if(request["method"] == "GET"):
		body = ""

		with open("./webpage/html/index.html", mode="r", encoding="utf-8") as pageSrc:
			# thinking to read in as binary?
			body = pageSrc.read()

		return httpMSG.response(status="200", body=body)

	elif(request["method"] == "POST"):
		# temporary same as GET
		body = ""

		with open("./webpage/html/index.html", mode="r", encoding="utf-8") as pageSrc:
			# thinking to read in as binary?
			body = pageSrc.read()

		return httpMSG.response(status="200", body=body)

	else:
		# error
		return httpMSG.response(status="200", body=f"Invalid request method : {request['method']}")

myHTTPmessage.PageHandlers.register("/", index)


myHTTPmessage.PageHandlers.listHandlers()

# ===============

# ===============

# func

def client_conn(ClientSock: socket.socket, ClientAddr: str): #ClientInfo:tuple[socket.socket, str]

	print(f"<INFO> New connection from: {ClientAddr}")

	# monitor input event by select
	sel = selectors.DefaultSelector()

	sel.register(ClientSock, selectors.EVENT_READ) # last param => default action (not used here)

	# log user info to global table ex. online

	while not toShutDown:
		httpMSG = myHTTPmessage.myHTTPmessage()

		if(len(sel.select(1)) > 0): # since only monitor 1 socket => (has something == can read)
			req = ClientSock.recv(MSGSIZE_MAX)

			if(len(req) == 0):
				# connection closed
				# jump out of loop and handle
				break

			req = myHTTPmessage.parseRequest(req.decode(encoding="utf-8"))

			print(" # ============================================== # \n")

			print(req)

			print("\n # ============================================== # \n\n")

			# use PageHandler
			ClientSock.sendall(myHTTPmessage.PageHandlers.routing(route=req["target"])(req, httpMSG))
			
	
	# connection closed
	print(f"<INFO> Connection from {ClientAddr} closed")

	sel.unregister(ClientSock)

	ClientSock.close()

	sel.close()

	return

def server_start(ServerAddr = "localhost"):
	ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	ServerSock.bind((ServerAddr, SERVER_PORT))

	print(f"<INFO> Server start: start listening on port {SERVER_PORT}...")
	ServerSock.listen(MAXCONN)

	return ServerSock

# ===============

if __name__ == "__main__": # main func
	ServerSock = server_start()
	
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
					print("<INFO> Server is going to shut down...")
					toShutDown = True
				else:
					print(f"<ERR> Unknown command : {cmd}")

		# join dead thread
		for conn in client_threads:
			if not conn.is_alive():
				conn.join()

				client_threads.remove(conn)

	# print("<INFO> Server shutting down...")

	for conn in client_threads:
		conn.join()

	# print("<INFO> Threads all joined")

	ServerSock.close()

	sel.unregister(ServerSock)

	sel.close()

	print("<INFO> Server shutted down.")

# main:

# toShutDown = true

# selector