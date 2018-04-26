import datetime
import time
import copy

# decorator function for creating singleton classes
def singleton(_myClass):
	tasks = {}
	# this task is not the one in project but the task of the singleton class
	def getInstance(*args, **kwargs):
		if _myClass not in tasks:
			tasks[_myClass] = _myClass(*args, **kwargs)
		return tasks[_myClass]
	return getInstance

@singleton
class Constants(object):
	'''Configuration based on xE.16x.large'''
	def __init__(self):
	self.numPrivateMachines = 20
	self.vcpuPrivate = 64
	self.disksPrivate = 1920
	self.memoryPrivate = 1952
	self.vcpuPublic = 64
	self.disksPublic = 1920
	self.memoryPublic = 1952
	self.avgVcpuForTask = 4
	self.maxVcpuForTask = 8
	self.maxMemForTask = 64
	self.maxDiskForTask = 64

class Machine(object):
    def __init__(self, name, vcpus, memory, disks):
    	# Name is random id of machine
        self.name = name
        self.memory = memory
        self.disks = disks
        self.vcpus = vcpus
        self.memoryFree = memory
        self.disksFree = disks
        self.vcpusFree = vcpus

class Task(object):
	def __init__(self, name, vcpus, memory, disks):
        self.name = name
        self.memory = memory
        self.disks = disks
        self.vcpus = vcpus

class CloudEngine(object):
	def __init__(self, vcpus, mem, disks):
		'''We have homogeneous cloud'''
		# Change this heap
		self.machineDict = {}
		self.vcpus = vcpus
		self.disks = disks
		self.memory = memory
		# incremental counter used for naming new machines
		self.idCounter = 0
	
	# adding machine to cloud
	def addServer(self):
		machine = Machine(self.idCounter, self.vcpus, self.memory, self.disks)
		self.idCounter += 1
		self.machineDict[name] = machine

	# check if machine can host the given task
	def can_host(self, machine, task):
		if machine.memory >= task.memory and machine.disks >= task.disks and machine.vcpus >= task.vcpus:
			return True
		return False

	def removeMachine(self, name):
		'''remove the given machine'''
		self.machineDict.pop(name, None)

@singleton
class Tasks(object):
	def __init__(self):
		self.inDict = {}

	def create(self, image, task, instanceName, machine):
		# code to create tasks
		info = {}
		info['image'] = image
		info['task'] = task
		info['instanceName'] = instanceName
		info['machine'] = machine
		self.inDict[instanceName] = info

		machine = CloudEngine()
		rack = Rack()
		# print machine.machineDict[machine]
		machine.updateServer(instanceName, task, machine, "add_instance")
		rack.updateRack(machine,image, 'add_instance')
		print "Task successfully created"
		# print machine.machineDict[machine]

	# deleting given task
	def delete(self, instanceName):
		machine = CloudEngine()
		rack = Rack()
		machine.updateServer(instanceName, self.inDict[instanceName]['task'], self.inDict[instanceName]['machine'], "del_instance")
		rack.updateRack(self.inDict[instanceName]['machine'], self.inDict[instanceName]['image'], "del_instance")
		del self.inDict[instanceName]

	# Print all running tasks
	def list(self):
		# print self.inDict
		if len(self.inDict) == 0:
			print "No Task Running"
			return

		for task in self.inDict:
			print "Task Name:", task,
			print ", Image:", self.inDict[task]['image'],
			print ", Task:", self.inDict[task]['task']

	def show(self):
		if len(self.inDict) == 0:
			print "No Task Running"
			return

		for task in self.inDict:
			print "Task Name:", task,
			print ", Machine:", self.inDict[task]['machine']

	def removeInstances(self, rack, task):
		# remove the image cache used by this task from rack
		# remove the task itself
		rack_obj = Rack()
		rack_obj.removeImageCache(rack, self.inDict[task]['image'])
		del self.inDict[task]
		pass

class CloudGateway(object):
	def __init__(self):
		self.publicCloud = CloudEngine

	def createPublicMachine(self):
		'''create public cloud machine'''
		pass

	def deletePublicMachine(self):
		'''delete public cloud machine'''
		pass

	def initialisePrivateCloud(self):
		'''initialise the public cloud'''
		pass

	def createRandomTask(self):
		'''create or delete a random task'''
		pass

	def getAverageUsage(self):
		'''returns the average CPU, disk and memory usage for public and private cloud'''
		pass

	def logAverageUsage(self):
		'''log the average CPU, disk and memory usage for public and private cloud'''
		pass

	def scheduleTask(self, task):
		'''decides if the task should be added to private or public cloud'''
		pass

	def checkMigrateToPrivate(self):
		'''check if migration to private is required'''
		pass

	def checkReorganisePublic(self):
		'''check if reorganization tasks in public cloud'''
		pass

	def migrateToPrivate(self):
		'''migrate tasks to private cloud from public cloud'''
		pass

	def reorganisePublic(self):
		'''reorganize tasks in public cloud to increase average usage'''
		pass

	def deleteTask(self, task):
		'''delete the task'''
		if checkMigrateToPrivate():
			migrateToPrivate()
		if checkReorganisePublic():
			reorganisePublic()

if __name__ == '__main__':
	log = open("cloudGatewayLog.txt","a")
	print "\n*************CloudEngine gateway simulation****************\n"
	interpreter = RandomTaskGeneration()
	# Numbe of add/delete tasks : X axis
	# Average % Usage : Y axis
	# Average CPU/Memory/Disk usage for both public and private cloud (6 lines)
	#print graph()
