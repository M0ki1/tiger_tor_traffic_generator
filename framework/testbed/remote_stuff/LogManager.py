import sys
import datetime
from os.path import exists
from dateutil.parser import parse
import re

class LogLine():
	timestamp : datetime
	message : str

	def __init__(self, line : str):
		try:
			self.timestamp = parse(line[:line.find(" - ")])
		except:
			self.timestamp = None
			pass
		self.message = line[line.find(" - "):]
		self.isStartSession = re.search("\*\*\*\* start_session", self.message)
		self.isEndSession = re.search("\*\*\*\* end_session (.*)", self.message)

class QueryLines():
	list_lines:list[LogLine]

	def __init__(self, list_lines:list[LogLine]):
		self.list_lines = list_lines

	def start_ts(self):
		res = None
		if len(self.list_lines) > 0:
			f = self.list_lines[0]
			res = f.timestamp
		return res
	
	def end_ts(self):
		res = None
		if len(self.list_lines) > 0:
			f = self.list_lines[-1]
			res = f.timestamp
		return res
		
class LogManager():
	logcontent: list[LogLine]

	def __init__(self, logfile):
		if exists(logfile):
			with open(logfile, "r") as f:
				lines = f.readlines()

				# self.logcontent = [LogLine(l) for l in lines if ...l.startsWithDatetime...]
				self.logcontent = []
				for l in lines:
					l1 = LogLine(l)
					if l1.timestamp:
						self.logcontent += [l1]

	def search(self, idx:int, type = "session"):
		res = list()
		for i,l in enumerate(self.logcontent):
			if f"{type}_{idx}" in l.message:
				res.append(l)
				for l_rev in self.logcontent[i+1:]:
					if f"{type}_{idx+1}" in l or f"{type}_{idx+1}" in l:
						break
					res.append(l_rev)
				break
		return QueryLines(res)
	
	def statistics(self, type = "session"): # TODO: do also "requests"
		startTs = list()
		endTs = list()
		pcapName = list()

		for l in self.logcontent:
			if l.isStartSession:
				startTs += [l.timestamp]
			elif l.isEndSession:
				endTs += [l.timestamp]
				pcapName += [l.isEndSession.group(1)]
		# breakpoint() # TODO: the last endTs is missing
		# assert(len(startTs) == len(endTs))
		diff = [(t2 - t1).total_seconds() for (t1,t2) in zip(startTs, endTs)]
		# print(f"len(startTs)={len(startTs)} len(endTs)={len(endTs)}")
		print(f"Max session duration is {max(diff)}s average is {sum(diff) / len(diff)}s")

	def search_request(self, request_idx:int):
		return self.search(request_idx, "request")
	
	def search_session(self, session_idx:int):
		return self.search(session_idx, "session")
	
	def get_last_session_info(self):
		return ""
	def get_last_request_info(self):
		return ""
	
class LogManagerClient(LogManager):

	def get_last_session_info(self):
		return self.get_last_info("sessions")
	
	def get_last_request_info(self):
		return self.get_last_info("requests")
	
	def get_last_info(self, str_search = "sessions"):
		self.logcontent.reverse()
		res = ""
		for l in self.logcontent:
			if f"{str_search} with average duration" in l:
				res = l
				break
		self.logcontent.reverse()
		return res
	
class LogManagerOS(LogManager):

	def get_last_session_info(self):
		return self.get_last_info("session")
	def get_last_request_info(self):
		return self.get_last_info("request")

	def get_last_info(self, str_search = "session"):
		self.logcontent.reverse()
		res = ""
		for idx,l in enumerate(self.logcontent):
			if (str_search == "session" and l.isEndSession) or "Stopping Traffic Capture" in l.message and "_request_" in l:
				t1 = l.timestamp
				for l2 in self.logcontent[idx+1:]:
					if (str_search == "session" and l.isStartSession) or "Starting Traffic Capture" in l2 and "_request_" in l2:
						t2 = l.timestamp
						res = f"last {str_search} took {(t2 - t1).total_seconds()}"
				break
		self.logcontent.reverse()
		return res

if __name__ == "__main__":
	log_manager = LogManager("file.log")
	is_client = True
	for idx,a in enumerate(sys.argv):
		if "--is-client" == a:
			is_client = True
		if "--is-os" == a:
			is_client = False
		if "--log-file" == a:
			del log_manager
			log_manager = LogManagerClient(sys.argv[idx+1]) if is_client else LogManagerOS(sys.argv[idx+1])
		if "--last-session-info" == a:
			res = log_manager.get_last_session_info()
			print(res)
		if "--last-request-info" == a:
			res = log_manager.get_last_request_info()
			print(res)
		if "--session" == a:
			res = log_manager.search_session(int(sys.argv[idx+1]))
			print(f"starts at {res.start_ts()} ends at {res.end_ts()}")
			for l in res.list_lines:
				print(l)
		if "--request" == a:
			res = log_manager.search_request(int(sys.argv[idx+1]))
			print(f"starts at {res.start_ts()} ends at {res.end_ts()}")
			for l in res.list_lines:
				print(l)
		if "--stats" == a:
			log_manager.statistics()

