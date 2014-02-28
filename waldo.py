import httplib
import json
import datetime

waldoserver = "waldo.rax.io"
DEBUG = False

def __digest_headers(httpreply):
	"""Convert httplib headers into dictionary"""
	headers = {}

	for item in httpreply.getheaders():
		headers[item[0]] = item[1]

	return headers

def __walk_collection_update(raw_coll):
	'''Walk through dictionary and convert data types
	'''

	for item in raw_coll:
		if isinstance(raw_coll,list) and (isinstance(item,dict) or isinstance(item,list)):
			raw_coll[raw_coll.index(item)] = __walk_collection_update(item)
		elif isinstance(raw_coll,dict):
			if isinstance(raw_coll[item],list) or isinstance(raw_coll[item],dict):
				raw_coll[item] = __walk_collection_update(raw_coll[item])
			else:
				if item == "time":
					date, time, offset = raw_coll[item].split(' ',2)

					date = date.split('-')
					time = time.split(':')

					raw_coll['time'] = datetime.datetime(int(date[0]), int(date[1]),int(date[2]),int(time[0]),int(time[1]),int(time[2]))

	return raw_coll

def __digest_json(raw_data):
	"""Convert some data elements in response to python types.
	"""

	data = json.loads(raw_data)

	data = __walk_collection_update(data)

	if DEBUG:
		data["raw_data"] = raw_data

	return data

def get_dossier(ddi=None,host=None,dossier=None):
	"""Call Get Dossier API function and process output
		URL: /api/<ddi>/dossiers/<host>/<dossier_id>

		Alternate #1: If passed with just dossier='' will call 'just_get_dossier' api
		URL: /api/dossiers/<dossier_id>

		Alternate #2: If passed with ddi='' and host='' without dossier, then
		will call 'get_latest_dossier' api function.
		URL: /api/<ddi>/dossiers/<host>/latest
	"""
	conn = httplib.HTTPSConnection(waldoserver)

	if not ddi is None and not host is None and not dossier is None:
		conn.request("GET", "/api/" + str(ddi) + "/dossiers/" + host + "/" + dossier)
	elif ddi is None and not dossier is None:
		conn.request("GET", "/api/dossiers/" + dossier)
	elif dossier is None and not ddi is None and not host is None:
		conn.request("GET", "/api/" + str(ddi) + "/dossiers/" + host + "/latest")
	else:
		#ERROR!
		return ("INVALID INPUT", None)
	

	reply = conn.getresponse()

	headers = __digest_headers(reply)

	result = {'headers': headers, 'status': (reply.status, reply.reason), 'dossier_id': dossier}

	if reply.status == 200:
		result['data'] = __digest_json(reply.read())
		result['dossier_id'] = result['data']['id']
		return ("FOUND", result)
	else:
		if DEBUG:
			result['raw_data'] = reply.read()
		return ("UNKNOWN", result)

def create_dossier(ddi,host):
	"""Perform Create Dossier API function and process output
		URL: /api/<ddi>/dossier/<host>
	
		If 302 response found, pass to get_dossier and present output
	"""
	conn = httplib.HTTPSConnection(waldoserver)

	conn.request("POST", "/api/" + str(ddi) + "/dossiers/" + host)

	reply = conn.getresponse()

	headers = __digest_headers(reply)

	result = {'headers': headers, 'status': (reply.status, reply.reason)}

	if not reply.status in (201,302):
		if DEBUG:
			result['raw_data'] = reply.read()
		return ("UNKNOWN",result)

	if reply.status == 201:
		result['data'] = __digest_json(reply.read())
		result['dossier_id'] = result['data']['id']
		return ("REQUESTED", result)

	if reply.status == 302:
		dossier_id = headers['location'].split(host + '/')[1]

		return get_dossier(ddi, host, dossier_id)

def get_dossier_list(ddi=None,host=None,offset=0,limit=25):
	"""Attempts to Perform get_dossier_list api call in one of three forms
		URL: /api/dossiers?offset=<offset>&limit=<limit>
		URL: /api/<ddi>/dossiers?offset=<offset>&limit=<limit>
		URL: /api/<ddi>/dossiers/<host>?offset=<offset>&limit=<limit>
	"""

	conn = httplib.HTTPSConnection(waldoserver)

	if host is None and not ddi is None:
		conn.request("GET","/api/" + str(ddi) + "/dossiers?offset=" + str(offset) + "&limit=" + str(limit))
	elif not host is None and not ddi is None:
		conn.request("GET", "/api/" + str(ddi) + "/dossiers/" + host + "?offset=" + str(offset) + "&limit=" + str(limit))
	else:
		conn.request("GET", "/api/dossiers?offset=" + str(offset) + "&limit=" + str(limit))

	reply = conn.getresponse()

	headers = __digest_headers(reply)

	result = {'headers': headers, 'status': (reply.status, reply.reason)}

	if reply.status == 200 or reply.status == 206:
		result['data'] = __digest_json(reply.read())

		if reply.status == 206:
			content_range = headers['content-range'].split(' ')[1].split('/')
			start, end = content_range[0].split('-')
			max = content_range[1]

			result['position'] = {'position': (int(start), int(end)), 'list-size': int(max)}
		else:
			result['position'] = {'position': (offset,offset + len(result['data'])), 'list-size': len(result['data'])}

		return ("SUCCESS", result)
	else:
		if DEBUG:
			result['raw_data'] = reply.read()
		return ("UNKNOWN", result)
