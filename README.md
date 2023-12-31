# CN_2023

Project of Computer Network 2023

# Usage

## PHASE 1  

### Setting environment

※ Linux platform (Ubuntu 20.04 used in test) should be able to run the program directly.
> But, please make sure you have:  
>
>> 1. make : ```apt install make```  
>> 2. g++  : ```apt install g++```  
>  
> Then, please ```cd``` into the directory "CN_2023/phase1" : ```cd CN_2023; cd phase1```  

※ For other platforms, please use [docker][1]:
P.S. For Windows, please use Powershell.
>
> 1. ```cd``` into the directory "CN_2023/phase1" : ```cd CN_2023; cd phase1```
> 2. Build the dockerfile into image : ```docker build -t cn2023_phase1 .```
> 3. Start the containter : ```docker run -it --rm cn2023_phase1```

### Run the program

Run ```make srun``` for running a server-end process  

> 1. The server process will listen on port 51966.  
> 2. To terminate the process, you may use Ctrl+C, or you can type "stop" in terminal.
  
Or ```make crun``` for a client-end one.  

> 1. The client-end process can only start after the server is on(or the process will just keep outputing something like ```socket(): connect() failed.```).
> 2. The server is assumed to operate on "ws3.csie.ntu.edu.tw"(NTUCSIE workstation 3), which is my development environment since I don't have other convenient domain name. If you would like to use your own hosts for server, please modify the default value of "serverHostName" at ```clienttool.hpp --> class CLNT_Socket --> socket_init(serverHostName)``` to "(name of your host)".  

### Personal profile website

Inside "phase1/profile/".

______

______

## PHASE 2

### Setting environment

#### Server Setup

Note: Please make sure that you have [docker][1] in advance.

```cd phase2```
> bash : ```./start_docker.sh```  
> powershell : ```.\start_docker.ps1```  

### Run the program

#### Server

After get into docker container, run ```./run.sh```  

The Server should run on port 51966 (the main URL for connection), 51967 (Web Server) and 51968 (Socket.io handler for phoning), where the latter 2 run isolatedly inside the docker (not accessible from the outside).  

PS. There might be some "newline" problem due to my poor setting of '.gitattribute', please fix them by ```sed``` or other tools you like. If you would like to help me fix the problem, please feel free to put messages on github (or put a request).  

#### Client

Connect to ```https://localhost:51966```, the webpage should be there.

By using nginx as reverse proxy, the webpage uses "https" and "persistent http", and has a single port for clients to use the whole services.  

[1]: https://www.docker.com/get-started/  
