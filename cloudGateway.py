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

    def canHost(vcpus, memory, disks):
        if self.memoryFree - memory >= 0.1 * self.memory and \
        self.disksFree - disks >= 0.1 * self.disks and \
        self.vcpusFree - vcpus >= 0.1 * self.vcpus:
            return True

class CloudEngine(object):
    def __init__(self, vcpus, memory, disks):
        '''We have homogeneous cloud'''
        self.machineHeap = []
        # Config of cloud
        self.vcpus = vcpus
        self.disks = disks
        self.memory = memory
        # incremental counter used for naming new machines
        self.idCounter = 0
        # percentage average
        self.avgMemoryUsage = 0
        self.avgVcpusUsage = 0
        self.avgDisksUsage = 0

    # adding machine to cloud
    def addServer(self):
        machine = Machine(self.idCounter, self.vcpus, self.memory, self.disks)
        self.idCounter += 1
        heappush(self.machineHeap, (machine.memoryFree, machine))

    # check if machine can host the given task
    def canHost(self, vcpus, memory, disks):
        for machine in machineHeap:
            if machine.canHost(vcpus, memory, disks):
                return True
        return False

    def updateTaskUsage(self, vcpus, memory, disks, public=False):
        '''update average usage of cloud engine'''
        self.avgVcpusUsage += (vcpus / self.vcpus) / len(machineHeap)
        self.avgMemoryUsage += (memory / self.memory) / len(machineHeap)
        self.avgDisksUsage += (disks / self.disks) / len(machineHeap)

    def removeMachine(self, name):
        '''remove the given machine'''
        for i, machine in enumerate(self.machineHeap):
            if machine.name == name:
                del self.machineHeap[i]
        heapify(self.machineHeap)

class Task(object):
    def __init__(self, name, vcpus, memory, disks, machine, public=False):
        self.name = name
        self.vcpus = vcpus
        self.memory = memory
        self.disks = disks
        self.public = False
        self.machine = machine

@singleton
class Tasks(object):
    def __init__(self):
        self.tasksList = []
        self.idCounter = 0

    def create(self, vcpus, memory, disks, public=False):
        # code to create tasks
        gateway = CloudGateway()
        if public:
            engine = gateway.publicCloud
        else:
            engine = gateway.privateCloud
        hostMachine = None
        for machine in engine.machineHeap:
            if machine.canHost(vcpus, memory, disks):
                hostMachine = machine
                task = Task(vcpus, memory, disks, hostMachine, public)
                return
        assert False, 'Task should be scheduled as canHost was checked for ' \
        'the engine before calling Tasks.create()'

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

    def canPrivateHost(self, vcpus, memory, disks):
        '''return true if average usage cpu usage of private is below threshold'''
        if self.privateCloud.avgVcpusUsage < 0.8 and \
        self.canPrivateHost.canHost(vcpus, memory, disks):
            return True
        return False

    def logAverageUsage(self):
        '''log the average CPU, disk and memory usage for public and private cloud'''
        pass

    def scheduleTask(self, vcpus, memory, disks):
        '''decides if the task should be added to private or public cloud'''
        self.tasksList.append(task)
        public = not self.canPrivateHost(vcpus, memory, disks)
        if public:
            engine = self.publicCloud
        else:
            engine = self.privateCloud
        tasks = Tasks()
        tasks.create(vcpus, memory, disks, public)
        engine.updateTaskUsage(vcpus, memory, disks)

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
