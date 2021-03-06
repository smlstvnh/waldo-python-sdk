__author__ = 'tmajibon'
__version__ = 0.1

import waldo

def get_host():
	valid_input = False

	while not valid_input:
		host = raw_input("Please enter domain or IP: ")

		host = host.strip(' ').lower().replace("https://","").replace("http://","").split('/')[0]

		if len(host) > 0:
			valid_input = True
		else:
			print "Invalid host input."
	return host

def get_ddi():
	valid_input = False

	while not valid_input:
		ddi = raw_input("Please enter DDI: ")

		ddi = ddi.strip(' ')

		if len(ddi) > 0 and ddi.isdigit():
			ddi = int(ddi)
			valid_input = True
		else:
			print "Invalid DDI Input."
	return ddi

def create_dossier():

	print "---------------------------------"
	print "Create Dossier"
	print "---------------------------------"
	print

	ddi = get_ddi()

	host = get_host()

	status, result = waldo.create_dossier(ddi,host)

	if status == "REQUESTED":
		print "Dossier requested, now generating:"
		print "\tID: " + result["dossier_id"]
	elif status == "FOUND":
		print "Existing Dossier found."
		print "\tID: " + result["dossier_id"]
		data = result['data']
		if data["discovery_status"] == "SUCCESS":
			print "\tTime: " + data['time'].isoformat()
			print "Tenant ID (DDI): " + data['tenant_id']
			print "\tNetwork Location: " + data['netlocl']
			print "\tResolved IP Address: " + data['resolved_ip_address']
			print "\tRegion: " + data['topology']['region']

	else:
		print "Invalid response, received " + str(result["status"][0]) + ": " + str(result["status"][1])

def get_dossier(dossier_id=None,ddi=None,host=None):
	print "---------------------------------"
	print "Retrieve Dossier"
	print "---------------------------------"
	print

	if dossier_id is None and (ddi is None and host is None):
		dossier_id = raw_input("Dossier ID> ").strip(' ')

	if not dossier_id is None:
		status, result = waldo.get_dossier(dossier=dossier_id)
	elif not ddi is None and not host is None:
		status, result = waldo.get_dossier(ddi=ddi,host=host)

	if status == "FOUND":
		data = result['data']
		print "Dossier retreived:"
		print "\tDossier ID: " + result['dossier_id']
		print "\tDiscovery Status: " + data["discovery_status"]
		if data["discovery_status"] == "SUCCESS":
			print "\tTime: " + data['time'].isoformat()
			print "\tTenant ID (DDI): " + data['tenant_id']
			print "\tNetwork Location: " + data['netloc']
			print "\tResolved IP Address: " + data['resolved_ip_address']
			print "\tRegion: " + data['topology']['region']
			print "\tSummary Page: https://" + waldo.waldoserver + "/gui#/" + data['tenant_id'] + "/dossiers/" + data['netloc'] + "/" + result['dossier_id'] + "/summary"
	else:
		print "Invalid response, received " + str(result["status"][0]) + ": " + str(result["status"][1])

def get_latest_dossier():
	print "---------------------------------"
	print "Retrieve Latest Dossier"
	print "---------------------------------"
	print

	get_dossier(ddi=get_ddi(),host=get_host())

def list_handler(ddi=None,host=None):
	offset = 0
	limit = 5
	listsize = 0

	while True:
		print "---------------------------------"

		status, results = waldo.get_dossier_list(ddi,host,offset,limit)

		if status == "SUCCESS":
			listsize = results['position']['list-size']

			data = results['data']

			if not len(data) > 0:
				print "No results found!"
				return

			for item in data:
				print str(data.keys().index(item)) + " *** Dossier: " + data[item]['id'] + " ***"
				print "\tDiscovery Status: " + data[item]['discovery_status']
				print "\tTime: " + data[item]['time'].isoformat()
				print "\tTenant ID (DDI): " + data[item]['tenant_id']
				print "\tNetwork Location: " + data[item]['netloc']

			print "---------------------------------"
			print "Showing " + str(offset) + " through " + str(offset + len(data)) + " of " + str(listsize)
			print "Page (" + str((offset/limit)+1) + "/" + str(listsize/limit) + ")"

			print "Select a dossier to retrieve, or one of the following options: "

			optionstr = ""

			if offset > 0:
				optionstr += "(p) Previous Page "
			if offset + limit < listsize:
				optionstr += "(n) Next Page "

			optionstr += '(x) Exit'

			print optionstr

			valid_input = False

			while not valid_input:
				choice = raw_input("> ")

				if len(choice) > 0:
					choice = choice[0].lower()

					if choice.isdigit():
						choice = int(choice)
						if choice >= 0 and choice < len(data):
							get_dossier(data[data.keys()[choice]]['id'])
						else:
							print "Invalid Selection."
					elif choice == 'p' and offset > 0:
						offset = offset - limit
						if offset < 0:
							offset = 0
						valid_input = True
					elif choice == 'n' and offset+limit < listsize:
						offset += limit
						valid_input = True
					elif choice == 'x':
						return
					else:
						print "Invalid Selection."

		else:
			print "Invalid response, received " + str(results["status"][0]) + ": " + str(results["status"][1])
			return

def find_dossier_by_DDI():
	print "---------------------------------"
	print "Get Dossier List By DDI"
	print "---------------------------------"
	print

	list_handler(ddi=get_ddi())


def find_dossier_by_DDI_HOST():
	print "---------------------------------"
	print "Get Dossier List By DDI"
	print "---------------------------------"
	print

	list_handler(ddi=get_ddi(),host=get_host())

def get_all_dossiers():
	print "---------------------------------"
	print "Get Dossier All Dossiers"
	print "---------------------------------"
	print
	list_handler()

def advanced_menu():
	while True:
		print "---------------------------------"
		print "Get Dossier List By DDI"
		print "---------------------------------"
		print
		print "Choose an option:"
		print "\t1) Get All Dossiers"
		print
		print "\tx) Exit"

		choice = raw_input("> ")

		if len(choice) > 0:
			choice = choice[0].lower()

			if choice == '1':
				get_all_dossiers()
			elif choice == 'x':
				return
			else:
				print "\nInvalid Input!\n"

keep_running = True

while keep_running:

	print "---------------------------------"
	print "Waldo Command Line Interface (v" + str(__version__) + ")"
	print "---------------------------------"
	print
	print "Choose an option:"
	print "\t1) Create Dossier"
	print "\t2) Get Dossier"
	print "\t3) Get Latest Dossier"
	print "\t4) Find Dossier by DDI"
	print "\t5) Find Dossier by DDI and Host"
	print "\t6) Advanced Options"
	print
	print "\tq) Quit"

	choice = raw_input("> ")

	if len(choice) > 0:
		choice = choice[0].lower()

		if choice == '1':
			create_dossier()
		elif choice == '2':
			get_dossier()
		elif choice == '3':
			get_latest_dossier()
		elif choice == '4':
			find_dossier_by_DDI()
		elif choice == '5':
			find_dossier_by_DDI_HOST()
		elif choice == '6':
			advanced_menu()
		elif choice == 'q':
			keep_running = False
		else:
			print "\nInvalid Input!\n"