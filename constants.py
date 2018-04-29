# Configuration based on xE.16x.large
numPrivateMachines = 20
vcpuPrivate = 64
disksPrivate = 1920
memoryPrivate = 1952
vcpuPublic = 64
disksPublic = 1920
memoryPublic = 1952
minVcpuForTask = 1
avgVcpuForTask = 4
maxVcpuForTask = 8
minMemForTask = 1
maxMemForTask = 64
minDiskForTask = 1
maxDiskForTask = 64

# other constants
deleteWithProbability = 10 # equivalent to 0.45
maxUtililizationPerMachine = 0.9 # equivalent to 90%
maxEngineUtilization = 0.8
minEngineUtilization = 0.5