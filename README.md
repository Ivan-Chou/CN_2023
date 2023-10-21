# CN_2023
Project of Computer Network 2023

# Usage
## Setting environment
※ Linux platform (Ubuntu 20.04 used in test) should be able to run the program directly, but please make sure you have:
> 1. make : ```apt install make```
> 2. g++  : ```apt install g++```<br/>

Then, please ```cd``` into the directory "CN_2023/phase1" : ```cd CN_2023 && cd phase1```<br/>

※ For other platforms, please use [docker][1]:
> 1. ```cd``` into the directory "CN_2023"
> 2. Build the dockerfile into image : ```cd ./phase1/Dockerfile && docker build -t cn2023_phase1 . && cd ../../```
> 3. Start the containter : ```docker run -it --rm -v ./phase1:/phase1 cn2023_phase1```

## Run the program
Run ```make srun``` for running a server-end process. <br/>
Or ```make crun``` for a clinet-end one.

[1]: https://www.docker.com/get-started/
