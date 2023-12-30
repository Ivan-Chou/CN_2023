import datetime
import gzip
import json
import re
from mylib.myMutltithread import atomic_print

# =====================================================

# func

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

def HTTPdate(later:float = 0.0):
	return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=later)).strftime("%a, %d %b %Y %H:%M:%S GMT")

def rawHTTPResponse(status="200", default_header:dict={}, temp_header:dict={}, body=""):
	"""return binary string for http response"""
	
	if(default_header == {}):
		default_header = {
			"Server"          : "None",
			"Vary"            : "Accept-Encoding",
			"Content-Encoding": "gzip",
			"Content-Type"    : "text/html;charset=UTF-8",
			"Keep-Alive"      : "timeout=5, max=100",
			"Connection"      : "Keep-Alive"
		}

	if(type(body) == bytes):
		body = gzip.compress(body)
	else:
		body = gzip.compress(body.encode("utf-8"))

	httpver = "1.1"

	headers = default_header.update(temp_header)

	headers = "\n".join([f"{key}: {headers[key]}" for key in headers])

	res = f"""HTTP/{httpver} {status}
Date: {HTTPdate()}
Content-Length: {len(body)}
{headers}

"""

	return (res.encode("utf-8") + body)

def render_html(html_str:str, alternative:dict[str, str]):
	"""
	Render html file.
	Find: "{{(something)}}" in html (like jinja).
	Substitute that string according to alternative. 
	"""

	for ele in alternative:
		html_str = alternative[ele].join(re.split(f"{{{{{ele}}}}}", html_str))

	return html_str

# =====================================================

class myHTTPmessage:
	""" a simple wrapper for http response written by myself """
	
	def __init__(self, status="200", init_header:dict[str, str]={}):
		self.httpver = "1.1"
		self.status = status
		self.header = {
			"Server"          : "None",
			"Vary"            : "Accept-Encoding",
			"Content-Encoding": "gzip",
			"Content-Type"    : "text/html;charset=UTF-8",
			"Keep-Alive"      : "timeout=5, max=100",
			"Connection"      : "Keep-Alive"
		}
		if(init_header != {}):
			self.header.update(init_header)

	def setStatus(self, status:str):
		self.status = status

	def setHeader(self, newHeaders:dict[str,str]):
		# append, remove
		for key in newHeaders:
			if(newHeaders[key] == "/rm"):
				if(key in self.header):
					self.header.pop(key)
			else:
				self.header[key] = newHeaders[key]

	def setContentType(self, ContentType:str):
		self.setHeader({"Content-Type": ContentType})

	def response(self, body=""):
		"""return binary string for http response"""

		if(isinstance(body, bytes)):
			body = gzip.compress(body)
		else:
			body = gzip.compress(body.encode("utf-8"))

		headers = "\n".join([f"{key}: {self.header[key]}" for key in self.header])

		res = f"""HTTP/{self.httpver} {self.status}
Date: {HTTPdate()}
Content-Length: {len(body)}
{headers}

"""

		return (res.encode("utf-8") + body)

DefaultFileUtil:dict[str, dict[str, any]] = {
	"plain" : {
		"location" : "",
		"response" : myHTTPmessage(init_header={"Content-Type" : "text/plain"})
	},
	"html" : {
		"location" : "./webpage/html/",
		"response" : myHTTPmessage()
	},
	"css" : {
		"location" : "./webpage/css/",
		"response" : myHTTPmessage(init_header={"Content-Type" : "text/css"})
	},
	"js" : {
		"location" : "./webpage/scripts/",
		"response" : myHTTPmessage(init_header={"Content-Type" : "text/javascript"})
	},
	"ico" : {
		"location" : "./webpage/icon/",
		"response" : myHTTPmessage(init_header={"Content-Type" : "image/ico"})
	},
	"json" : {
		"location" : "./webpage/json/",
		"response" : myHTTPmessage(init_header={"Content-Type" : "application/json"})
	}
}

class defaultHandlers:
	@staticmethod
	def response404(request:dict[str,str]):
		httpMSG = myHTTPmessage(status="404")
		return httpMSG.response(body="Such page is not founded")
	
	@staticmethod
	def default_GET(request:dict[str,str]):
		target = request["target"].split("/")[-1]

		if(target[-1] == "?"):
			# GET
			pass
		elif(target.split(".")[-1] in DefaultFileUtil):
			# html, css, javascript or some other things
			FileExt = target.split(".")[-1]

			body = ""

			with open(DefaultFileUtil[FileExt]["location"] + target, mode="rb") as src:
				body = src.read()

			return DefaultFileUtil[FileExt]["response"].response(body=body)
		else:
			return defaultHandlers.response404(request=request)

class pageHandler:
	""" the struct to store all the behavior to handle requests """

	def __init__(self):
		self.handlers = dict()

		self.handlers["default"] = defaultHandlers.default_GET

	def register(self, route:str, handler):
		self.handlers[ route ] = handler

	def listHandlers(self):
		atomic_print("\n".join([
			"<INFO> Listing route handlers:\n",
			"\n".join([f"route = \"{ele}\", handler name = \"{self.handlers[ele].__name__}\"" for ele in self.handlers]),
			"\n"
		]))

	def routing(self, route:str):
		if(route in self.handlers):
			return self.handlers[ route ]
		else:
			return self.handlers["default"]

# =====================================================

# global variables

PageHandlers = pageHandler()

# =====================================================
