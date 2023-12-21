import datetime
import gzip
import socket

from mylib import myHTTPmessage

# ===============

# macro

MSGSIZE_MAX = 1024

# ===============

# ===============

# handlers

def index(request):
	if(request["method"] == "GET"):
		pass

	elif(request["method"] == "POST"):
		pass

	else:
		# error
		pass
myHTTPmessage.PageHandlers.register("/", index)


myHTTPmessage.PageHandlers.listHandlers()

# ===============

ServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ServerSock.bind(("localhost", 8080))

print("<INFO> Start listening")
ServerSock.listen(5)

# each connection for a thread
(ClientSock, ClientAddr) = ServerSock.accept()

while True:
	if ((ClientSock, ClientAddr) == (None, None)):
		(ClientSock, ClientAddr) = ServerSock.accept()
		print(f"<INFO> New connection from: {ClientAddr}")

	req = ClientSock.recv(MSGSIZE_MAX)

	if(len(req) == 0):
		# connection closed
		print(f"<INFO> Connection {ClientAddr} closed")

		(ClientSock, ClientAddr) = (None, None)

		continue

	print(" # ============================================== # \n")

	print(myHTTPmessage.parseRequest(req.decode(encoding="utf-8")))

	print("\n # ============================================== # \n\n")

	msg = myHTTPmessage.myHTTPmessage()

	body = ""

	with open("./webpage/html/index.html", mode="r", encoding="utf-8") as pageSrc:
		# thinking to read in as binary?
		body = pageSrc.read()

	ClientSock.sendall(msg.response(status="200", body=body))

	# ClientSock.close()

# main:

# toShutDown = true

# selector