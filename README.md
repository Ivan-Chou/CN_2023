# CN_2023
Project of Computer Network 2023

# Usage
## Setting environment
※ Linux platform (Ubuntu 20.04 used in test) should be able to run the program directly.
> But, please make sure you have:  
>> 1. make : ```apt install make```  
>> 2. g++  : ```apt install g++```  
>  
> Then, please ```cd``` into the directory "CN_2023/phase1" : ```cd CN_2023; cd phase1```  

※ For other platforms, please use [docker][1]:
P.S. For Windows, please use Powershell.
> 1. ```cd``` into the directory "CN_2023/phase1" : ```cd CN_2023; cd phase1```
> 2. Build the dockerfile into image : ```docker build -t cn2023_phase1 .```
> 3. Start the containter : ```docker run -it --rm cn2023_phase1```

## Run the program
Run ```make srun``` for running a server-end process. <br/>
Or ```make crun``` for a clinet-end one.

# Personal profile website
Inside "phase1/profile/".

[1]: https://www.docker.com/get-started/
