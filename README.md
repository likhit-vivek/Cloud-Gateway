# Cloud Gateway
Aditya Gujral (726004085), Piyush Bhatt (227002733), Likhit Vivek Chirumamilla (325001774)

## Timeline
We worked for approximately 27 hrs over a span of 7 days from 25 Apr 2018 to 1 May 2018.

## Project Specification
Our project focuses on implementing the seamless integration/transfer of tasks from a private cloud to a public cloud when the private cloud overloads over a specific limit. For this purpose, we are simulating a private cloud with a fixed number of homogeneous machines and created a script which generates tasks randomly to overload the private cloud. The usage of each of the machines as well as the average usage of the whole private cloud is being continuously monitored and as soon as the average usage goes over 80%, we are moving the tasks to one of the active machines in the public cloud. To reduce fragmentation, we are using Heaps to store the tasks and machines in an order, within the code, so that the tasks can be assigned/rearranged efficiently.

This kind of hybrid cloud service will be really useful in solving the problem of load balancing during peak times.

## Background Research
We looked at how AWS is using load-based instances to rapidly start or stop machines and how Amazon CloudWatch is being used to continuously monitor the workload metrics like average CPU usage and Memory consumption to upscale and downscale automatically in response to the varying input traffic. Our project is also implemented similarly, as we are balancing the load in our private cloud just like AWS, in its public cloud, the only difference being, we are additionally moving the tasks from private to public cloud.

We had to consider the issue of fragmentation and understand how to use Heaps to handle the proper assignment and rearrangement of tasks. 

We also understood how Azure implemented its horizontal and vertical auto-scaling but felt that the AWS model suits our project better and decided on similar design choices.

## Design Choices

#### Full Ownership
We are assuming that we own both the private and the public cloud so that, we are responsible for taking care of all the load-balancing and defragmentation ourselves, unlike the case of using AWS, as it'll do all the optimization automatically and our project would be meaningless. 

We are also assuming that we are using this cloud internally i.e. we are only dealing with the tasks from our employees, not our users. Although we are randomly generating the tasks, it's not completely random. We are using some constraints like growth rate, max size of a task with respect to machine capacity etc. So, it's only logical that we have a complete knowledge on the kind of workload we need to handle which is why we are using the cloud internally.

#### Homogeneous Cloud
One of the important choices we made is that, we are running a homogeneous datacenter i.e. We have all the software stack we need and all the machines are alike. That way it'll be easier to monitor the usage of each of the machines and prevent fragmentation when moving the tasks from one machine to the other, from private to public cloud or within the public cloud.

#### Unlimited resources in Public Cloud
To handle any kind of workload, we are assuming we have unlimited resources in our public cloud. So, theoretically, we can keep on adding the tasks and will never run out of machines. But at the same time, we don't want to be inefficient. So, we chose the AWS model, where the machines are started or stopped on demand, and we are assuming that only the active machines will consume power. To improve the efficiency further, we are ensuring that the usage of the public cloud doesn't fall below 50%, by rearranging the tasks when more of the machines are being sparsely used.

#### Max and Min load
Just like AWS, we are placing a threshold on the average usage of both private and public clouds to handle sudden spikes in the workload and also to increase efficiency. For example, if the private cloud usage crosses 80%, we are going to move some tasks to the public cloud, and if it goes under 50%, we are moving the tasks from the public cloud back to the private cloud. Additionally, if the usage in the public cloud goes under 50%, we are moving the tasks to only a few machines within the public, and stopping the machines which become empty, thus increasing the usage. We are also keeping track of each of the machines and ensuring that each machine has at least 10% of free resources at any point of time.

#### Machine specs vs Task requirements

#### Using Heaps for defragmentation

#### Migration back to Private cloud

## Implementation

## Instructions
* Use python 2.7
* Extract the project file and navigate to the folder in cmd (Windows)
* Run ```python cloudGateway.py```

## Lessons Learned and Conclusion

## References
* [Load-based Scaling in AWS](https://docs.aws.amazon.com/opsworks/latest/userguide/workinginstances-autoscaling-loadbased.html)
* [Auto-scaling in Azure](https://docs.microsoft.com/en-us/azure/architecture/best-practices/auto-scaling)
* Our P1 code
