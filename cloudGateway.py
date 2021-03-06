from __future__ import division
from random import randint
from heapq import heappush, heappop, heapify
import constants
from copy import deepcopy
import pandas as pd
import matplotlib.pyplot as plt
import constants

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
        self.totalMemoryUsage = 0
        self.totalVcpusUsage = 0
        self.totalDisksUsage = 0

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
            self.totalVcpusUsage += vcpus
            self.totalMemoryUsage += memory
            self.totalDisksUsage += disks
        else:
            self.totalVcpusUsage -= vcpus
            self.totalMemoryUsage -= memory
            self.totalDisksUsage -= disks
            assert self.totalVcpusUsage >= 0, 'Total vcpu usage less than 0'
            assert self.totalMemoryUsage >= 0, 'Total memory usage less than 0'
            assert self.totalDisksUsage >= 0, 'Total disk usage less than 0'

    def removeMachine(self, name):
        '''remove the given machine'''
        for index, machineTuple in enumerate(self.machineHeap):
            machine = machineTuple[1]
            if machine.name == name:
                del self.machineHeap[index]
        heapify(self.machineHeap)

    def deleteFreeMachines(self):
        '''delete public cloud machine'''
        if len(self.machineHeap) <= 1:
            return
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
        self.public = public
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
                
                machine.vcpusFree -= vcpus
                machine.memoryFree -= memory
                machine.disksFree -= disks
                return
        assert False, 'Task should be scheduled as canHost was checked for ' \
        'the engine before calling Tasks.create()'

    def delete(self, index):
        '''deleting given task and returns the engine task was deleted from'''
        self.tasksList[index].machine.vcpusFree += self.tasksList[index].vcpus
        self.tasksList[index].machine.memoryFree += self.tasksList[index].memory
        self.tasksList[index].machine.disksFree += self.tasksList[index].disks
        return self.tasksList.pop(index)

@singleton
class CloudGateway(object):
    def __init__(self):
        self.privateCloud = CloudEngine(constants.vcpuPrivate, constants.memoryPrivate, constants.disksPrivate)
        self.publicCloud = CloudEngine(constants.vcpuPublic, constants.memoryPublic, constants.disksPublic)
        # initialize the private cloud
        for _ in range(constants.numPrivateMachines):
            self.privateCloud.addServer()
        # initialize the public cloud
        self.publicCloud.addServer()
    
    def canPublicHost(self, vcpus, memory, disks):
        '''check if public cloud requires additional machine for task to be scheduled'''
        if self.publicCloud.totalVcpusUsage / len(self.publicCloud.machineHeap) < constants.maxEngineUtilization and \
        self.publicCloud.canHost(vcpus, memory, disks):
            return True
        return False

    def canPrivateHost(self, vcpus, memory, disks):
        '''return true if average usage cpu usage of private is below threshold'''
        if self.privateCloud.totalVcpusUsage / len(self.privateCloud.machineHeap) < constants.maxEngineUtilization and \
        self.privateCloud.canHost(vcpus, memory, disks):
            return True
        return False

    def logAverageUsage(self):
        '''log the average CPU, disk and memory usage for public and private cloud'''
        privateMachineLen = len(self.privateCloud.machineHeap)
        publicMachineLen = len(self.publicCloud.machineHeap)
        log = ' '.join([str(self.privateCloud.totalVcpusUsage / privateMachineLen),
                        ', ', str(self.privateCloud.totalMemoryUsage / privateMachineLen),
                        ', ', str(self.privateCloud.totalDisksUsage / privateMachineLen),
                        ', ', str(self.publicCloud.totalVcpusUsage / publicMachineLen),
                        ', ', str(self.publicCloud.totalMemoryUsage / publicMachineLen),
                        ', ', str(self.publicCloud.totalDisksUsage / publicMachineLen),
                        ', ', str(publicMachineLen), '\n'])
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
        if self.privateCloud.totalVcpusUsage / len(self.privateCloud.machineHeap) < constants.minEngineUtilization:
            return True
        return False

    def checkDefragPublic(self):
        '''check if reorganization tasks in public cloud'''
        if self.publicCloud.totalVcpusUsage / len(self.publicCloud.machineHeap) < constants.minEngineUtilization:
            return True
        return False

    def migrateToPrivate(self):
        '''migrate tasks to private cloud from public cloud'''
        tasks = Tasks()
        sortedTasks = deepcopy(sorted(tasks.tasksList, key=lambda x: x.vcpus, reverse=True))
        for task in sortedTasks:
            if task.public and self.canPrivateHost(task.vcpus, task.memory, task.disks):
                for index, x in enumerate(tasks.tasksList):
                    if x.name == task.name:
                        tasks.delete(index)
                        self.publicCloud.updateTaskUsage(task.vcpus, task.memory, task.disks, False)
                        tasks.create(task.vcpus, task.memory, task.disks, public=False)
                        self.privateCloud.updateTaskUsage(task.vcpus, task.memory, task.disks, True)

    def defragPublic(self):
        '''reorganize tasks in public cloud to increase average usage'''
        tasks = Tasks()
        sortedTasks = deepcopy(sorted(tasks.tasksList, key=lambda x: x.vcpus, reverse=True))
        for task in sortedTasks:
            if task.public:
                for index, x in enumerate(tasks.tasksList):
                    if x.name == task.name:
                        tasks.delete(index)
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
        memory = randint(constants.minMemForTask, constants.maxMemForTask)
        disks = randint(constants.minDiskForTask, constants.maxDiskForTask)
        vcpus = randint(constants.minVcpuForTask, constants.maxVcpuForTask)
        gateway = CloudGateway()
        gateway.scheduleTask(vcpus, memory, disks)

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
    logFile = open('cloudGatewayLog.csv', 'w')
    log = ''.join(['Average private Cpu usage,', 
                    'Average private memory usage,',
                    'Average private disks usage,',
                    'Average public Cpu usage,',
                    'Average public memory usage,',
                    'Average public disks usage,',
                    'Number of public machines\n'])
    logFile.write(log)
    taskGenerator = RandomTaskGeneration()
    for operation in range(100000):
        taskGenerator.executeRandomTask()
    taskGenerator = RandomTaskGeneration()
    constants.deleteWithProbability = 60
    for operation in range(10000):
        taskGenerator.executeRandomTask()
    constants.deleteWithProbability = 40
    for operation in range(10000):
        taskGenerator.executeRandomTask()
    # Numbe of add/delete tasks : X axis
    # Average % Usage : Y axis
    # Average CPU/Memory/Disk usage for both public and private cloud
    #print graph()
    data = pd.read_csv('cloudGatewayLog.csv')
    data['Average private Cpu usage'] = data['Average private Cpu usage'] * 100 / constants.vcpuPrivate
    data['Average public Cpu usage'] = data['Average public Cpu usage'] * 100 / constants.vcpuPublic
    plt.xlabel('Iteration')
    plt.ylabel('Percentage usage')
    plt.title('Increased growth followed by decreased and increased growth')
    plt.plot(data.index.tolist(), data['Average private Cpu usage'], label='Average private Cpu usage')
    plt.plot(data.index.tolist(), data['Average public Cpu usage'], label='Average public Cpu usage')
    plt.legend(loc='lower right')
    plt.savefig('averageCpuUsage.png')
    plt.gcf().clear()
    plt.xlabel('Iteration')
    plt.ylabel('Number of machines')
    plt.title('Increased growth followed by decreased and increased growth')
    plt.plot(data.index.tolist(), data['Number of public machines'], label='Number of public machines')
    plt.legend(loc='lower right')
    plt.savefig('numMachines.png')
    print 'exiting'
