srun: ./svr_b
	./svr_b

crun: ./clnt_b
	./clnt_b "ws3.csie.ntu.edu.tw:51966"

svr_b: ./server.cpp
	g++ -O2 -o svr_b ./server.cpp

clnt_b: ./client.cpp
	g++ -O2 -o clnt_b ./client.cpp

clean:
	rm ./*_b