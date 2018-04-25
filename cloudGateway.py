import datetime
import time
import copy

# log status
# st = None

# decorator function for creating singleton classes
def singleton(_myClass):
	instances = {}
	# this instance is not the one in project but the instance of the singleton class
	def getInstance(*args, **kwargs):
		if _myClass not in instances:
			instances[_myClass] = _myClass(*args, **kwargs)
		return instances[_myClass]
	return getInstance



@singleton
class Rack(object):
	def __init__(self):
		self.rkDict = {}
	
	# function to create rack of given storage
	def createRack(self, rackName, storage):
		rack = {}
		rack['rackName'] = rackName
		rack['storage'] = storage
		rack['status'] = 'healthy'
		rack['servers'] = []
		rack['imagecaches'] = []
		self.rkDict[rackName] = rack

	# function to add servers to racks and change their status to healthy
	def addMachine(self, server, rack):
		self.rkDict[rack]['servers'].append(server)
		self.rkDict[rack]['status'] = 'healthy'

	# funciton to remove machine from its rack
	def removeMachine(self, rack, server):
		# print self.rkDict
		self.rkDict[rack]['servers'].remove(server)

	# function to remove the image from the rack
	def removeImageCache(self, rack, image):
		im = Images()
		# self.rkDict[rack]['storage'] += im.imDict[image]['size']
		self.rkDict[rack]['imagecaches'].remove(image)
		pass

	# Check if the rack containing the give server can hold the given image
	def canRackHold(self, server, image):
		hardware = Hardware()
		im = Images()
		rack = hardware.hwDict[server]['rack']
		
		if self.rkDict[rack]['storage'] >= im.imDict[image]['size']:
			print "Rack", rack, "has space to cache image", image
			return True
		else:
			print "Rack", rack, "do not have space to cache", image
			return False

	# update the rack in case an image is deleted or added to the rack storage
	def updateRack(self, server, image, operation):
		hardware = Hardware()
		im = Images()

		rack = hardware.hwDict[server]['rack']
		
		if operation == 'add_instance':
			# self.rkDict[rack]['storage'] -= im.imDict[image]['size']
			self.rkDict[rack]['imagecaches'].append(image)

		elif operation == "del_instance":
			# self.rkDict[rack]['storage'] += im.imDict[image]['size']
			self.rkDict[rack]['imagecaches'].remove(image)
	
	# show the rack information
	def show(self, rackName):
		print "Image Caches in rack", rackName, ":"
		if len(self.rkDict[rackName]['imagecaches']) == 0:
			print "No image caches in rack ",rackName
		for image in self.rkDict[rackName]['imagecaches']:
			print image

	# evacuate the rack successfully
	def evacuate(self, rackName):
		# save all instances of the rack
		# delete all machines on this rack
		# delete this rack
		# reallocate all the instances if possible otherwise
		
		if rackName not in self.rkDict.keys():
			print "Invalid Rack Name!"
			raise Exception("Invalid Rack Name!")
		
		inst = Instances()
		hardware = Hardware()

		# 1----> save all instances of the rackName
		deletedInstances = {}
		for serv in self.rkDict[rackName]['servers']:
			instances = hardware.hwDict[serv]['instances']
			for thisInstance in instances:
				deletedInstances[thisInstance] = inst.inDict[thisInstance]

		# 2----> print deletedInstances
		# delete all instances from machine and delete that machine from rack 
		deleteServers = copy.deepcopy(self.rkDict[rackName]['servers'])
		for serv in deleteServers:
			# print deleteServers
			hardware.removeMachine(serv)
			print "Server", serv, "successfully removed"

		# 3----> delete the rack
		del self.rkDict[rackName]

		#  4----> Reallocate all the instances in other racks
		interpreter = Interpreter()
		for instanceName in deletedInstances:
			img = deletedInstances[instanceName]['image']
			flvr = deletedInstances[instanceName]['flavor']
			success = False
			for hw in hardware.hwDict:
				cmd = "aaggiestack admin can_host " + hw + " " + flvr
				cmd = cmd.split()
				print "Can <", instanceName, "> relocate  to <", hw,"> ....",
				if interpreter.admin(cmd, False) == 1 and self.canRackHold(hw,img):
					success = True
					inst.create(img, flvr, instanceName, hw)
					print instanceName," RELOCATED TO", hw 
					break
			# If no server found
			if success == False:
				print "WARNING! COULD NOT RELOCATE", instanceName



@singleton
class Hardware(object):
	def __init__(self):
		self.hwDict = {}
		self.hwOriginalDict = {}
	
	# adding server to the given rack
	def addServer(self, details):
		hw = {}
		hw['name'] = details.split()[0]
		hw['rack'] = details.split()[1]
		hw['ip'] = details.split()[2]
		hw['mem'] = int(details.split()[3])
		hw['num-disks'] = int(details.split()[4])
		hw['num-cores'] = int(details.split()[5])
		hw['instances'] = []
		
		if hw['name'] in self.hwDict.keys():
			print("Server already exists!")
			raise Exception("Server already exists!")
		
		self.hwDict[details.split()[0]] = hw

		# also update rack info in rack object
		rack = Rack()
		rack.addMachine(hw['name'], hw['rack'])
		self.hwOriginalDict[details.split()[0]] = details

	def config(self, fileName):
		# code to read data and save configurations
		with open(fileName, "r") as f:
			hardware = f.readlines()
		iterHW = iter(hardware)

		# read and store rack information from hdwr file
		rack = Rack()
		no_of_racks = int(next(iterHW))
		for count in range(no_of_racks):
			line = next(iterHW)
			rack.createRack(line.split()[0], int(line.split()[1]))

		next(iterHW)

		# saving configuration for all machines in the dictionary
		for line in iterHW:
			self.addServer(line)

	def adminShow(self):
		print len(self.hwDict)
		for key in self.hwDict.keys():
			print self.hwDict[key]

	def show(self):
		print len(self.hwOriginalDict)
		for key in self.hwDict.keys():
			print self.hwOriginalDict[key]

	# check if server can host the given flavor
	def can_host(self, server, flavor):
		machine = self.hwDict[server]
		machineMem = machine['mem']
		machineDisk = machine['num-disks']
		machineVcpus = machine['num-cores']

		flavorMem = flavor['mem']
		flavorDisk = flavor['num-disks']
		flavorVcpus = flavor['num-cores']

		if machineMem >= flavorMem and machineDisk >= flavorDisk and machineVcpus >= flavorVcpus:
			print "Yes"
			return 1
		print "No"
		return 0


	# updating the values of server
	def updateServer(self, instanceName, flavor, server, operation):
		machine = self.hwDict[server]
		machineMem = machine['mem']
		machineDisk = machine['num-disks']
		machineVcpus = machine['num-cores']

		flvr = Flavors()
		flavor = flvr.flDict[flavor]
		flavorMem = flavor['mem']
		flavorDisk = flavor['num-disks']
		flavorVcpus = flavor['num-cores']

		if operation == "add_instance":
			machineMem -= flavorMem
			machineDisk -= flavorDisk
			machineVcpus -= flavorVcpus
			self.hwDict[server]['instances'].append(instanceName)

		elif operation == "del_instance":
			machineMem += flavorMem
			machineDisk += flavorDisk
			machineVcpus += flavorVcpus
			self.hwDict[server]['instances'].remove(instanceName)

		self.hwDict[server]['mem'] = machineMem
		self.hwDict[server]['num-disks'] = machineDisk
		self.hwDict[server]['num-cores'] = machineVcpus

	# remove the given server
	def removeMachine(self, server):
		# remove the images used by instances in this machine
		# remove instances in this machine
		# remove this machine from the rack
		if server not in self.hwDict.keys():
			print("No such server!")
			raise Exception("No such server!")
		
		rack = Rack()
		instance = Instances()
		for inst in self.hwDict[server]['instances']:
			instance.removeInstances(self.hwDict[server]['rack'], inst)
		rack.removeMachine(self.hwDict[server]['rack'], server)
		del self.hwDict[server]
		pass



@singleton
class Images(object):
	def __init__(self):
		self.imDict = {}

	def config(self, fileName):
		# code to read data and save configurations
		with open(fileName, "r") as f:
			images = f.readlines()
		iterIM = iter(images)
		next(iterIM)
		
		# saving configuration for all images in the dictionary
		for line in iterIM:
			im = {}
			im['name'] = line.split()[0]
			im['size'] = int(line.split()[1])
			im['path'] = line.split()[2]
			self.imDict[line.split()[0]] = im
			# self.imDict[line.split()[0]] = line

	def show(self):
		print len(self.imDict)
		for key in self.imDict.keys():
			print self.imDict[key]['name'] , self.imDict[key]['size'], self.imDict[key]['path']


@singleton
class Flavors(object):
	def __init__(self):
		self.flDict = {}

	def config(self, fileName):
		# code to read data and save configurations
		with open(fileName, "r") as f:
			flavors = f.readlines()
		iterFL = iter(flavors)
		next(iterFL)
		
		# saving configuration for all machines in the dictionary
		for line in iterFL:
			fl = {}
			fl['name'] = line.split()[0]
			fl['mem'] = int(line.split()[1])
			fl['num-disks'] = int(line.split()[2])
			fl['num-cores'] = int(line.split()[3])
			self.flDict[line.split()[0]] = fl
			# self.flDict[line.split()[0]] = line

	def show(self):
		print len(self.flDict)
		for key in self.flDict.keys():
			print self.flDict[key]['name'], self.flDict[key]['mem'], self.flDict[key]['num-disks'], self.flDict[key]['num-cores']


@singleton
class Instances(object):
	def __init__(self):
		self.inDict = {}

	def create(self, image, flavor, instanceName, server):
		# code to create instances
		info = {}
		info['image'] = image
		info['flavor'] = flavor
		info['instanceName'] = instanceName
		info['server'] = server
		self.inDict[instanceName] = info

		hardware = Hardware()
		rack = Rack()
		# print hardware.hwDict[server]
		hardware.updateServer(instanceName, flavor, server, "add_instance")
		rack.updateRack(server,image, 'add_instance')
		print "Instance successfully created"
		# print hardware.hwDict[server]

	# deleting given instance
	def delete(self, instanceName):
		hardware = Hardware()
		rack = Rack()
		hardware.updateServer(instanceName, self.inDict[instanceName]['flavor'], self.inDict[instanceName]['server'], "del_instance")
		rack.updateRack(self.inDict[instanceName]['server'], self.inDict[instanceName]['image'], "del_instance")
		del self.inDict[instanceName]

	# Print all running instances
	def list(self):
		# print self.inDict
		if len(self.inDict) == 0:
			print "No Instance Running"
			return

		for instance in self.inDict:
			print "Instance Name:", instance,
			print ", Image:", self.inDict[instance]['image'],
			print ", Flavor:", self.inDict[instance]['flavor']

	def show(self):
		if len(self.inDict) == 0:
			print "No Instance Running"
			return

		for instance in self.inDict:
			print "Instance Name:", instance,
			print ", Server:", self.inDict[instance]['server']

	def removeInstances(self, rack, instance):
		# remove the image cache used by this instance from rack
		# remove the instance itself
		rack_obj = Rack()
		rack_obj.removeImageCache(rack, self.inDict[instance]['image'])
		del self.inDict[instance]
		pass


# Interprets the commands and runs the respective module
class Interpreter(object):
	
	# taking care of config commands to aggiestack
	def config(self, command ):
		global st
		# self.st = None
		if len(command) == 4:
			
			if command[2][0:2] == "--":
				
				if command[2] == "--hardware":
					
					try:
						hardware = Hardware()
						hardware.config(command[3])
						st  = st + "SUCCESS!\n"
					except:
						print "ERROR! Command execution failed"
						st = st + "FAILURE\n"
				
				elif command[2] == "--images":
					
					try:
						images = Images()
						images.config(command[3])
						st  = st + "SUCCESS!\n"
					except:
						print "ERROR! Command execution failed"
						st = st + "FAILURE\n"
				
				elif command[2] == "--flavors":
					
					try:
						flavors = Flavors()
						flavors.config(command[3])
						st  = st + "SUCCESS!\n"
					except:
						print "ERROR! Command execution failed"
						st = st + "FAILURE\n"
				
				else:
					print "ERROR! Command execution failed"
					st = st + "FAILURE\n"
			
			else:
				print "ERROR! \"--\" expected"
				st = st + "FAILURE\n"
		
		else:
			print "ERROR! Incorrect parameters!"
			st = st + "FAILURE\n"
		

	# taking care of show commands to aggiestack
	def show(self, command):
		global st
		if len(command) == 3:
			try:	
				if command[2] == "hardware":
					hardware = Hardware()
					hardware.show()
					st  = st + "SUCCESS!\n"
					
				elif command[2] == "images":
					images = Images() 
					images.show()
					st  = st + "SUCCESS!\n"
					
				elif command[2] == "flavors":
					flavors = Flavors() 
					flavors.show()
					st  = st + "SUCCESS!\n"

				elif command[2] == "all":
					hardware = Hardware()
					images = Images()
					flavors = Flavors()
					hardware.show()
					images.show()
					flavors.show()
					st  = st + "SUCCESS!\n"

				else:
					print "ERROR! Invalid parameter: ", command[2]
					st  = st + "FAILURE!\n"

			except:
				print "ERROR! Failure to retrive desired info"
				st  = st + "FAILURE!\n"
		else:
			print "ERROR! Incorrect parameters!"
			st  = st + "FAILURE!\n"

	# taking care of admin commands to aggiestack
	def admin(self, command, modify_st = True):
		global st
		successFlag = 0;
		try:
			# modify this if according to P1
			if command[2] == "show": 
				if command[3] == "hardware":
			 		hardware = Hardware()
					hardware.adminShow()
					st  = st + "SUCCESS!\n"

				elif command[3] == "instances":
					instance = Instances()
					instance.show()
					st = st + "SUCCESS!\n"

				elif command[3] == "imagecaches":
					rack = Rack()
					rack.show(command[4])
					st = st + "SUCCESS!\n"

				else:
					print "ERROR! Invalid parameter: ", command[3]
					st = st + "FAILURE\n"

			
			elif command[2] == "can_host":
				hardware = Hardware()
				flavors = Flavors()
				flavor = flavors.flDict[command[4]]
				successFlag = hardware.can_host(command[3], flavor)
				if modify_st:
					st  = st + "SUCCESS!\n"
				return successFlag


			elif command[2] == "evacuate":
				rack = command[3]
				rack_obj = Rack()
				rack_obj.evacuate(rack)
				
				st  = st + "SUCCESS!\n"
			

			elif command[2] == "remove":
				hardware = Hardware()
				hardware.removeMachine(command[3])
				print "Server", command[3], "successfully removed"
				st  = st + "SUCCESS!\n"


			elif command[2] == "add":
				if len(command) == 14:	
				
					if command[3] == "--mem":
						mem = command[4]
							
						if command[5] == "--disk":
							disk = command[6]

							if command[7] == "--vcpus":
								vcpus = command[8]

								if command[9] == "--ip":
									ip = command[10]

									if command[11] == "--rack":
										rack = command[12]
										machine = command[13]

										update = machine + " " + rack + " " + ip + " " + mem + " " + disk + " " + vcpus + "\n"
										hardware_obj = Hardware()
										hardware_obj.addServer(update)

										print "New machine <",machine,"> added to rack <",rack,">"
										st = st + "SUCCESS!\n"
										
									else:
										print "ERROR! Invalid parameter: ", command[11]
										st = st + "FAILURE\n"
								else:
									print "ERROR! Invalid parameter: ", command[9]
									st = st + "FAILURE\n"
							else:
								print "ERROR! Invalid parameter: ", command[7]
								st = st + "FAILURE\n"
						else:
							print "ERROR! Invalid parameter: ", command[5]
							st = st + "FAILURE\n"
					else:
						print "ERROR! Invalid parameter: ", command[3]
						st = st + "FAILURE\n"
				else:
					print "ERROR! Incorrect parameters!"
					st = st + "FAILURE\n"
			
			else:
				print "ERROR! Invalid Syntax"
				if modify_st:
					st += "FAILURE\n"

		except:
			print "ERROR! Unsuccessful command execution!"
			st += "FAILURE\n"

	# taking care of server commands to aggiestack
	def server(self, command):
		global st
		if command[2] == "create":
			
			if len(command) == 8:	
				
				if command[3] == "--image":
					img = command[4]
						
					if command[5] == "--flavor":
						flvr = command[6]
						instanceName = command[7]

						try:
							instance = Instances()
							hardware_obj = Hardware()
							rack_obj = Rack()
							hwDict = hardware_obj.hwDict

							# check if istance is not already running
							for hw in hwDict:
								if instanceName in hwDict[hw]['instances']:
									print "ERROR! This instance is already running!"
									raise Exception("instance error")

							# Find a server which can fit given flavor and store it
							success = False
							for hw in hwDict:
								cmd = "aggiestack admin can_host " + hw + " " + flvr
								cmd = cmd.split()
								print "Checking if server <", hw, "> can store flavor <", flvr,"> ....",
								if self.admin(cmd, False) == 1:
									# if rack_obj.canRackHold(hw,img):
									success = True
									instance.create(img, flvr, instanceName, hw)
									break


							# If no server found
							if success == False:
								print "ERROR! NO MORE AVAILABLE RESOURCES"

							# hardware.config(command[3])
							st  = st + "SUCCESS!\n"
						except:
							print "ERROR! Invalid Instance, flavor or/and image name(s)."
							st = st + "FAILURE\n"
					else:
						print "ERROR! Invalid parameter: ", command[5]
						st = st + "FAILURE\n"
				else:
					print "ERROR! Invalid parameter: ", command[3]
					st = st + "FAILURE\n"
			else:
				print "ERROR! Incorrect parameters!"
				st = st + "FAILURE\n"
		


		elif command[2] == "delete":
			
			if len(command) == 4:
				instanceName = command[3]
				
				try:
					instance = Instances()
					instance.delete(instanceName)
					print "Instance <", instanceName, "> deleted"
					st  = st + "SUCCESS!\n"
					pass
				
				except:
					print "ERROR! No instance named: ", command[3]
					st = st + "FAILURE\n"

			else:
				print "ERROR! Incorrect parameters!"
				st = st + "FAILURE\n"
		



		elif command[2] == "list":
			
			if len(command) == 3:
				instance = Instances()
				instance.list()
				st = st + "SUCCESS\n"

			else:
				print "ERROR! Incorrect parameters!"
				st = st + "FAILURE\n"


		else:
			print "ERROR! Invalid Syntax"
			st += "FAILURE\n"

	def help(self):
		with open("help.txt", "r") as f:
			help = f.readlines()
		for line in help:
			print line

	# calls the respective modules according to the head of the command
	def executeCommand(self,command):
		# getting timestamp for logging purpose
		global st
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		st = "["+st+"]\n";
		st = st + "".join(command) + "\n";

		command = command.split()
		# calling corresponding function according to the command	
		
		if command[0] == "help":
			self.help()
		elif command[1] == "config":
			self.config(command );
		elif command[1] == "show":
			self.show(command );
		elif command[1] == "admin":
			self.admin(command );
		elif command[1] == "server":
			self.server(command);
		else:
			print "ERROR! Invalid Syntax!"
			st = st + "ERROR! Invalid Syntax!\n"
		
# execution starts here
if __name__ == '__main__':
	
	global st

	log = open("aggiestack-log.txt","a")
	print "\n*************AGGIESTACK CLI****************\n"
	interpreter = Interpreter()
	command = raw_input("Enter the command (input q to quit):")

	while(command != 'q'):
		if len(command) > 0:
			st = None
			interpreter.executeCommand(command)
			# write command execution status in log 
			log.write(st + "\n")
			log.flush()
		command = raw_input("Enter the command (input q to quit):")
	# interpreter.executeCommand('aggiestack config --hardware hdwr-config.txt')
	# # interpreter.executeCommand('aggiestack show hardware')
	# interpreter.executeCommand('aggiestack config --images image-config.txt')
	# # interpreter.executeCommand('aggiestack show images')
	# interpreter.executeCommand('aggiestack config --flavors flavor-config.txt')
	# # interpreter.executeCommand('aggiestack show flavors')
	# # interpreter.executeCommand('aggiestack show all')
	# # interpreter.executeCommand('aggiestack admin show hardware')

	# # interpreter.executeCommand('aggiestack admin show instances')
	# # interpreter.executeCommand('aggiestack admin can_host m1 xlarge')
	
	# interpreter.executeCommand('aggiestack server create --image linux-ubuntu --flavor xlarge INSTANCE_NAME')
	# # interpreter.executeCommand('aggiestack admin show hardware')
	# # interpreter.executeCommand('aggiestack server delete INSTANCE_NAME')
	# # interpreter.executeCommand('aggiestack admin show imagecaches r2')
	# # interpreter.executeCommand('aggiestack server list')
	# interpreter.executeCommand('aggiestack admin show instances')
	# interpreter.executeCommand('aggiestack admin add --mem 128 --disk 64 --vcpus 64 --ip 128.0.0.1 --rack r2 newmachine')
	# # interpreter.executeCommand('aggiestack admin show hardware')
	# # interpreter.executeCommand('aggiestack admin remove newmachine')
	# interpreter.executeCommand('aggiestack server create --image linux-ubuntu --flavor xlarge INSTANCE_NAME2')
	
	# # interpreter.executeCommand('aggiestack admin remove newmachine')
	# interpreter.executeCommand('aggiestack admin show instances')
	# interpreter.executeCommand('aggiestack admin evacuate r2')
		