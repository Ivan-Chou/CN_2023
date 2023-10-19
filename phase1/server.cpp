#include <sys/socket.h>
#include <unistd.h>
#include <stdio.h>
#include <arpa/inet.h>
// for sockaddr_in
#include <netinet/in.h>
// for TCP_NODELAY
#include <netinet/tcp.h>
// for bzero()
#include <string.h>
#include <poll.h>

#include <cctype>
#include <thread>
#include <iostream>
#include <vector>
#include <string>

#include "cafetool.hpp"

using namespace std;

bool toShutDown = false; // not necessary to have a lock

void client_func(int);

void server_func(int*);

int main(int argc, char const *argv[])
{
    int server_ret = 0;
    thread thrd_server(server_func, &server_ret);

    string main_name("CMD");
    
    string cmd = "";

    while(true){
        cmd = "";
        cin >> cmd;

        if(cmd == "stop"){ // modified to map<command, func> later
            toShutDown = true;
            
            cout << InfoMsg(main_name, "server is going to shutdown...");

            thrd_server.join();

            break;
        }
        else{
            cout << InfoMsg(main_name, string("Command \"") + cmd + string("\" has no implementation yet..."));
        }
    }

    cout << InfoMsg(main_name, "server shutted down.");

    return 0;
}

class Client{
    public:
    int sock_fd;
    FILE* sock_file;
    string name;

    Client(int fd){
        sock_fd = fd;        
        sock_file = fdopen(fd, "r+");
        setvbuf(sock_file, nullptr, _IONBF, 0);

        name = "";
    }

    ~Client(){
        if(sock_file){
            fclose(sock_file);
        }
    }

    // going to remove, call fscanf(clnt.sock_file, ...) directly instead
    ssize_t sock_fscanf(char* recv_format, char* buf){
        return fscanf(sock_file, recv_format, buf);
    }

    ssize_t sock_recv(char* buf){
        return recv(sock_fd, buf, strlen(buf), 0);
    }

    // IO should be at here
    ssize_t sock_send(char* str){
        return send(sock_fd, str, strlen(str), 0);
    }
};

void client_func(int fd){
    if(fd < 0) return;

    Client clnt(fd);

    // the length assertion should be done in client.cpp as well
    char buf_name[MAX_NAME_LEN + 1] = "";

// have to check whether there is a duplicate name in online users 
    char recv_format[MSG_BUFMAX] = "";
    sprintf(recv_format, "%%%ds", MAX_NAME_LEN);
    // fscanf(clnt.sock_file, recv_format, buf_name);

    clnt.sock_fscanf(recv_format, buf_name);

    clnt.name = string(buf_name);

    cout << InfoMsg("client_func()", string("New client name = ") + clnt.name);

    // modify later
    char greeting[MSG_BUFMAX] = "";
    sprintf(greeting, "Hello from CAFE server, %s !\n", buf_name);

    clnt.sock_send(greeting);
    
    // cout << InfoMsg("client_func()", string("Greet written to ") + clnt.name);

    cout << InfoMsg("client_func()", string("Client name = ") + clnt.name + string(" connection closed"));
    
    return;
}

void server_func(int* ret_ptr){
    SVR_Socket svr_socket;

    string server("Server");
    
    cout << InfoMsg(server, "Starting...");

    if(svr_socket.socket_init()){
        *ret_ptr = 1;
        return;
    }

    char msg[MSG_BUFMAX] = "";
    sprintf(msg, "Operating with socket fd = %d", svr_socket.ListenSocket_fd);

    cout << InfoMsg(server, msg);

    vector<thread> thrd_clients;

    while(!toShutDown){
        // clean disconnected thrds

        if(svr_socket.has_request()){
            cout << InfoMsg(server, "Received new connection");

            int client_fd = svr_socket.accept_request();
            
            if(client_fd > 0){
                thrd_clients.push_back(thread(client_func, client_fd));
            }
        }
    }

    // shutting down -> join all client thread
    while(!thrd_clients.empty()){
        thrd_clients.back().join();
        thrd_clients.pop_back();
    }

    cout << InfoMsg(server, "Terminated.");

    *ret_ptr = 0;
    return;
}

/*
class online_info
*/