from random import randint
from heapq import heappush, heappop, heapify
import constants
from copy import deepcopy

logFile = open('cloudGateWayLog.txt', 'w')
# decorator function for creating singleton classes
def singleton(_myClass):
    tasks = {}
    # this task is not the one in project but the task of the singleton class
    def getInstance(*args, **kwargs):
        if _myClass not in tasks:
            tasks[_myClass] = _myClass(*args, **kwargs)
        return tasks[_myClass]
    return getInstance

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

    def canHost(self, vcpus, memory, disks):
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

    def addServer(self):
        '''adding machine to cloud'''
        machine = Machine(self.idCounter, self.vcpus, self.memory, self.disks)
        self.idCounter += 1
        heappush(self.machineHeap, (machine.memoryFree, machine))

    def canHost(self, vcpus, memory, disks):
        '''check if machine can host the given task'''
        for _, machine in self.machineHeap:
            if machine.canHost(vcpus, memory, disks):
                return True
        return False

    def updateTaskUsage(self, vcpus, memory, disks, create=True):
        '''update average usage of cloud engine'''

        if create:
            self.avgVcpusUsage += (vcpus / self.vcpus) / len(self.machineHeap)
            self.avgMemoryUsage += (memory / self.memory) / len(self.machineHeap)
            self.avgDisksUsage += (disks / self.disks) / len(self.machineHeap)
        else:
            self.avgVcpusUsage -= (vcpus / self.vcpus) / len(self.machineHeap)
            self.avgMemoryUsage -= (memory / self.memory) / len(self.machineHeap)
            self.avgDisksUsage -= (disks / self.disks) / len(self.machineHeap)
            assert self.avgVcpusUsage >= 0, 'Average vcpu usage less than 0'
            assert self.avgMemoryUsage >= 0, 'Average memory usage less than 0'
            assert self.avgDisksUsage >= 0, 'Average disk usage less than 0'

    def removeMachine(self, name):
        '''remove the given machine'''
        for index, machineTuple in enumerate(self.machineHeap):
            machine = machineTuple[1]
            if machine.name == name:
                del self.machineHeap[index]
        heapify(self.machineHeap)

    def deleteFreeMachines(self):
        '''delete public cloud machine'''
        for index, machineTuple in enumerate(self.machineHeap):
            machine = machineTuple[1]
            if machine.vcpusFree == machine.vcpus:
                del self.machineHeap[index]
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
        '''code to create tasks'''
        gateway = CloudGateway()
        engine = gateway.publicCloud if public else gateway.privateCloud
        hostMachine = None
        for _, machine in engine.machineHeap:
            if machine.canHost(vcpus, memory, disks):
                hostMachine = machine
                task = Task(self.idCounter, vcpus, memory, disks, hostMachine, public)
                self.tasksList.append(task)
                self.idCounter += 1
                return
        assert False, 'Task should be scheduled as canHost was checked for ' \
        'the engine before calling Tasks.create()'

    def delete(self, index):
        '''deleting given task and returns the engine task was deleted from'''
        return self.tasksList.pop(index, None)

@singleton
class CloudGateway(object):
    def __init__(self):
        self.publicCloud = CloudEngine(constants.vcpuPrivate, constants.memoryPrivate, constants.disksPrivate)
        self.privateCloud = CloudEngine(constants.vcpuPublic, constants.memoryPublic, constants.disksPublic)
        # initialize the private cloud
        for _ in range(constants.numPrivateMachines):
            self.privateCloud.addServer()
    
    def canPublicHost(self, vcpus, memory, disks):
        '''check if public cloud requires additional machine for task to be scheduled'''
        if self.publicCloud.avgVcpusUsage < constants.maxEngineUtilization and \
        self.publicCloud.canHost(vcpus, memory, disks):
            return True
        return False

    def canPrivateHost(self, vcpus, memory, disks):
        '''return true if average usage cpu usage of private is below threshold'''
        if self.privateCloud.avgVcpusUsage < constants.maxEngineUtilization and \
        self.privateCloud.canHost(vcpus, memory, disks):
            return True
        return False

    def logAverageUsage(self):
        '''log the average CPU, disk and memory usage for public and private cloud'''
        log = ' '.join(['Average private Cpu usage, ', self.privateCloud.avgVcpusUsage,
                        ', Average private memory usage, ', self.privateCloud.avgMemoryUsage,
                        ', Average private disks usage, ', self.privateCloud.avgDisksUsage,
                        ', Average public Cpu usage, ', self.publicCloud.avgVcpusUsage,
                        ', Average public memory usage, ', self.publicCloud.avgMemoryUsage,
                        ', Average public disks usage, ', self.publicCloud.avgDisksUsage,
                        ', Number of public machines, ', len(self.publicCloud.machineHeap)])
        logFile.write(log)

    def scheduleTask(self, vcpus, memory, disks):
        '''decides if the task should be added to private or public cloud'''
        public = not self.canPrivateHost(vcpus, memory, disks)
        engine = self.publicCloud if public else self.privateCloud
        tasks = Tasks()
        if not self.canPublicHost(vcpus, memory, disks):
            self.publicCloud.addServer()
        tasks.create(vcpus, memory, disks, public)
        engine.updateTaskUsage(vcpus, memory, disks)
        self.logAverageUsage()

    def checkMigrateToPrivate(self):
        '''check if migration to private is required'''
        if self.privateCloud.avgVcpusUsage < constants.minEngineUtilization:
            return True
        return False

    def checkDefragPublic(self):
        '''check if reorganization tasks in public cloud'''
        if self.publicCloud.avgVcpusUsage < constants.minEngineUtilization:
            return True
        return False

    def migrateToPrivate(self):
        '''migrate tasks to private cloud from public cloud'''
        tasks = Tasks()
        for task in sorted(tasks.tasksList):
            if task.public and self.canPrivateHost(task.vcpus, task.memory, task.disks):
                tasks.delete(task.name)
                self.publicCloud.updateTaskUsage(task.vcpus, task.memory, task.disks, False)
                tasks.create(task.vcpus, task.memory, task.disks, public=False)

    def defragPublic(self):
        '''reorganize tasks in public cloud to increase average usage'''
        tasks = Tasks()
        sortedTasks = deepcopy(sorted(tasks.tasksList))
        for task in sortedTasks:
            if task.public:
                tasks.delete(task.name)
                tasks.create(task.vcpus, task.memory, task.disks, public=True)
        self.publicCloud.deleteFreeMachines()

    def deleteTask(self, index):
        '''delete the task at given index'''
        tasks = Tasks()
        deletedTask = tasks.delete(index)
        if self.checkMigrateToPrivate():
            self.migrateToPrivate()
        if self.checkDefragPublic():
            self.defragPublic()
        
        engine = self.publicCloud if deletedTask.public else self.privateCloud
        engine.updateTaskUsage(deletedTask.vcpus, deletedTask.memory, deletedTask.disks, False)
        self.logAverageUsage()

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
        deleteTask = True if randint(1, 100) <= constants.deleteWithProbability else False
        
        tasks = Tasks()
        if len(tasks.tasksList) == 0:
            deleteTask = False
            
        if deleteTask:
            numTasks = len(tasks.tasksList)
            deleteIndex = randint(0, numTasks - 1)
            gateway = CloudGateway()
            gateway.deleteTask(deleteIndex)
        else:
            self.generateRandomTask()

if __name__ == '__main__':
    print '\n*************CloudEngine gateway simulation*************\n'
    # starting cloud gateway
    CloudGateway()
    
    taskGenerator = RandomTaskGeneration()
    for operation in range(1000):
        taskGenerator.executeRandomTask()
    # Numbe of add/delete tasks : X axis
    # Average % Usage : Y axis
    # Average CPU/Memory/Disk usage for both public and private cloud
    #print graph()
