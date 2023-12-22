import datetime
import gzip
import json
from mylib.myMutltithread import atomic_print

def parseRequest(request):
	# parse the request (utf-8) to a dictionary

	request = request.split("\r\n")

	# atomic_print(request)

	ret = dict()

	# 1st line: http metadata
	req_line0 = request[0].split(" ")
	if(len(req_line0) != 3):
		# totally empty packet is observed => close connection
		atomic_print(f"<EXCE> parseRequest(): request[0] --> {request[0]}")
		ret["firstline"] = request[0]
	else:
		(ret["method"], ret["target"], ret["ver"]) = req_line0

	# then: header
	lineCnt = 1 # the line that has been processed, for the need of determining body

	for ele in request[1:]:
		lineCnt += 1

		if(ele == ""):
			break

		ele = ele.split(": ")

		if(len(ele) <= 1):
			atomic_print(f"<EXCE> parseRequest(): ele --> {ele}")
			break

		ret[ ele[0] ] = ele[1]

	# last: body
	ret["body"] = "\n".join(request[ lineCnt : ])

	return ret

def parseRequestBody(ContentType: str, body: str) -> dict[str:str]:
	res = dict()
	
	if(ContentType == "application/json"):
		res = json.loads(body)
	else:
		res = dict([ele.split("=") for ele in body.split("&")])

	return res

def parseCookie(cookie:str):
	return dict([ele.split("=") for ele in cookie.split(", ")])

# =====================================================

class myHTTPmessage:
	""" a simple wrapper for http response written by myself """
	
	def __init__(self):
		self.httpver = "1.1"
		self.ContentType = "text/html;charset=UTF-8"
		self.header = {
			"Server"          : "None",
			"Vary"            : "Accept-Encoding",
			"Content-Encoding": "gzip",
			"Content-Type"    : "text/html;charset=UTF-8",
			"Keep-Alive"      : "timeout=5, max=100",
			"Connection"      : "Keep-Alive"
		}

	def setHeader(self, key:str, value:str):
		# append, remove
		if(value == "/rm"):
			if(key in self.header):
				self.header.pop(key)
		else:
			self.header[key] = value

	def response(self, status="200", body="", type="str"):
		# return binary string for http response

		# consider to open the html files at here
		if(type == "bin"):
			body = gzip.compress(body)
		else:
			body = gzip.compress(body.encode("utf-8"))

		headers = "\n".join([f"{key}: {self.header[key]}" for key in self.header])

		res = f"""HTTP/{self.httpver} {status}
Date: {datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}
Content-Length: {len(body)}
{headers}

"""

		return (res.encode("utf-8") + body)

DefaultFileInfo = {
	"css" : {
		"location" : "./webpage/css/",
		"Content-Type" : "text/css"
	},
	"js" : {
		"location" : "./webpage/scripts/",
		"Content-Type" : "text/javascript"
	},
	"html" : {
		"location" : "./webpage/html/",
		"Content-Type" : "text/javascript"

	},
	"ico" : {
		"location" : "./webpage/icon/",
		"Content-Type" : "image/ico"
	}
}

class defaultHandlers:
	@staticmethod
	def response404(request:dict, httpMSG:myHTTPmessage):
		return httpMSG.response(status="404", body="Such page is not founded")
	
	@staticmethod
	def default_GET(request:dict, httpMSG:myHTTPmessage):
		target = request["target"].split("/")[-1]

		if(target[-1] == "?"):
			# GET
			pass
		elif(target.split(".")[-1] in DefaultFileInfo):
			# html, css, javascript or some other things
			specificMSG = myHTTPmessage() 

			FileExt = target.split(".")[-1]

			body = ""

			with open(DefaultFileInfo[FileExt]["location"] + target, mode="rb") as src:
				body = src.read()

			specificMSG.setHeader("Content-Type", DefaultFileInfo[FileExt]["Content-Type"])

			return specificMSG.response(status="200", body=body, type="bin")
		else:
			return defaultHandlers.response404(request=request, httpMSG=httpMSG)

class pageHandler:
	""" the struct to store all the behavior to handle requests """

	def __init__(self):
		self.handlers = dict()

		self.handlers["default"] = defaultHandlers.default_GET

	def register(self, route:str, handler):
		self.handlers[ route ] = handler

	def listHandlers(self):
		atomic_print("<INFO> Listing route handlers:\n")
		
		for ele in self.handlers:
			atomic_print(f"route = \"{ele}\", handler name = \"{self.handlers[ele].__name__}\"")
		
		atomic_print("\n")

	def routing(self, route:str):
		if(route in self.handlers):
			return self.handlers[ route ]
		else:
			return self.handlers["default"]

# =====================================================

# global variables

PageHandlers = pageHandler()

# =====================================================



# req_ex = """POST / HTTP/1.1
# Host: localhost:8080
# Connection: keep-alive
# Content-Length: 11
# Cache-Control: max-age=0
# sec-ch-ua: "Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"
# sec-ch-ua-mobile: ?0
# sec-ch-ua-platform: "Windows"
# Upgrade-Insecure-Requests: 1
# Origin: http://localhost:8080
# Content-Type: application/x-www-form-urlencoded
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
# Sec-Fetch-Site: same-origin
# Sec-Fetch-Mode: navigate
# Sec-Fetch-User: ?1
# Sec-Fetch-Dest: document
# Referer: http://localhost:8080/login?
# Accept-Encoding: gzip, deflate, br
# Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7

# ID_PW=hello"""

# if __name__ == "__main__":

# 	# atomic_print(f"{parseRequest(request=req_ex)}")

# 	msg = myHTTPmessage()

# 	msg.setHeader(key="cookie", value="hello")

# 	atomic_print(f"{msg.response(status='200', body='ACK!')}")

# 	msg.setHeader(key="cookie", value="/rm")

# 	atomic_print(f"{msg.response(status='200', body='ACK!')}")
