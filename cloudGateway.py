from random import randint
from heapq import heappush, heappop, heapify

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

        # other constants
        self.deleteWithProbability = 45 # equivalent to 0.45
        self.maxUtililizationPerMachine = 0.9 # equivalent to 90%

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

class CloudEngine(object):
    def __init__(self, vcpus, memory, disks):
        '''We have homogeneous cloud'''
        # Change this heap
        self.machineHeap = []
        self.vcpus = vcpus
        self.disks = disks
        self.memory = memory
        # incremental counter used for naming new machines
        self.idCounter = 0
        self.avgMemory = 0
        self.avgVcpu = 0
        self.avgDisks = 0

    # adding machine to cloud
    def addServer(self):
        machine = Machine(self.idCounter, self.vcpus, self.memory, self.disks)
        self.idCounter += 1
        heappush(self.machineHeap, (machine.memoryFree, machine))

    # check if machine can host the given task
    def canHost(self, machine, task):
        if machine.memoryFree - task.memory >= 0.1 * machine.memory and \
        machine.disksFree - task.disks >= 0.1 * machine.disks and \
        machine.vcpusFree - task.vcpus >= 0.1 * machine.vcpus:
            return True
        return False

    def removeMachine(self, name):
        '''remove the given machine'''
        for i, machine in enumerate(self.machineHeap):
            if machine.name == name:
                del self.machineHeap[i]
        heapify(self.machineHeap)

class Task(object):
    def __init__(self, name, vcpus, memory, disks, public=False):
        self.name = name
        self.vcpus = vcpus
        self.memory = memory
        self.disks = disks
        self.public = False
        self.machine = None

@singleton
class Tasks(object):
    def __init__(self):
        self.tasksList = []
        self.idCounter = 0

    def create(self, vcpus, memory, disks, public=False):
        # code to create tasks
        task = Task(vcpus, memory, disks, public)

    # deleting given task
    def delete(self, index):
        del self.tasksList[index]

@singleton
class CloudGateway(object):
    def __init__(self):
        constants = Constants()
        self.publicCloud = CloudEngine(constants.vcpuPrivate, constants.memoryPrivate, constants.disksPrivate)
        self.privateCloud = CloudEngine(constants.vcpuPublic, constants.memoryPublic, constants.disksPublic)

    def createPrivateMachine(self):
        '''create public cloud machine'''
        pass

    def createPublicMachine(self):
        '''create public cloud machine'''
        pass

    def deletePublicMachine(self):
        '''delete public cloud machine'''
        pass

    def initialisePrivateCloud(self):
        '''initialize the public cloud'''
        constants = Constants()
        for _ in range(constants.numPrivateMachines):
            self.createPrivateMachine()

    def getAverageUsage(self):
        '''returns the average CPU, disk and memory usage for public and private cloud'''
        pass

    def canPrivateHost(self):
        '''return true if average usage cpu usage of private is below threshold'''
        pass

    def logAverageUsage(self):
        '''log the average CPU, disk and memory usage for public and private cloud'''
        pass

    def scheduleTask(self, vcpus, memory, disks):
        '''decides if the task should be added to private or public cloud'''
        if public:
            engine = self.publicCloud
        else:
            engine = self.privateCloud
        self.tasksList.append(task)
        public = self.canPrivateHost()
        tasks = Tasks()
        tasks.create(vcpus, memory, disks)

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

    def deleteTask(self, index):
        '''delete the task at given index'''
        if self.checkMigrateToPrivate():
            self.migrateToPrivate()
        if self.checkReorganisePublic():
            self.reorganisePublic()
        tasks = Tasks()
        tasks.delete(deleteIndex)

class RandomTaskGeneration:
    def generateRandomTask(self):
        '''create random task for scheduling'''
        memory = randint(1, 8)
        disk = randint(1, 64)
        vcpus = randint(1, 8)
        gateway = CloudGateway()
        gateway.scheduleTask(memory, disk, vcpus)

    def executeRandomTask(self):
        '''create or delete a random task'''
        constants = Constants()
        deleteTask = True if randint(1, 100) <= constants.deleteWithProbability else False
        tasks = Tasks()
        if deleteTask:
            numTasks = len(tasks.tasksList)
            deleteIndex = randint(0, numTasks - 1)
            gateway = CloudGateway()
            gateway.deleteTask(deleteIndex)
        else:
            self.generateRandomTask()

if __name__ == '__main__':
    log = open("cloudGatewayLog.txt", "a")
    print "\n*************CloudEngine gateway simulation****************\n"
    interpreter = RandomTaskGeneration()
    # Numbe of add/delete tasks : X axis
    # Average % Usage : Y axis
    # Average CPU/Memory/Disk usage for both public and private cloud     #print graph()
