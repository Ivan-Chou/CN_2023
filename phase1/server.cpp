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

// 0xCAFE
#define SVR_PORT 51966
// ms, for poll()
#define WAITTIME 1000
// the max length of an user's name
#define MAX_NAME_LEN 15

using namespace std;

bool toShutDown = false; // not necessary to have a lock

string InfoMsg(string, string);

string ErrMsg(string, string, string);

string DebugMsg(string, string);

class mySocket;

class Client;

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

string InfoMsg(string parent, string toSay){
    return (string("<INFO> ") + parent + string(": ") + toSay + string("\n"));
}

string ErrMsg(string parent, string func, string detail = ""){
    return (string("<ERR> ") + parent + string(": ") + func + string(" failed") + (detail == "" ? string(".") : (string(", ") + detail)) + string("\n"));
}

string DebugMsg(string parent, string toSay){
    return (string("<DEBUG> ") + parent + string(": ") + toSay + string("\n"));
}

class mySocket{
    public:
    int ListenSocket_fd;

    mySocket(){
        ListenSocket_fd = -1;
    }

    ~mySocket(){
        if(ListenSocket_fd > 2){
            close(ListenSocket_fd); 
        }
    }

    int socket_init(){
        ListenSocket_fd = socket(AF_INET, SOCK_STREAM, 0);

        if(ListenSocket_fd < 0){
            cerr << ErrMsg("socket_init()", "socket()");
            return 1;
        }

        int tmp = 1;
        if (setsockopt(ListenSocket_fd, SOL_SOCKET, SO_REUSEADDR, (void*)&tmp, sizeof(tmp)) < 0) {
            cerr << ErrMsg("socket_init()", "setsockopt()");
            return 1;
        }
        
        struct sockaddr_in servaddr;

        bzero(&servaddr, sizeof(servaddr));
        servaddr.sin_family = AF_INET;
        servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
        servaddr.sin_port = htons(SVR_PORT);

        if (bind(ListenSocket_fd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0) {
            cerr << ErrMsg("socket_init()", "bind()");
            return 1;
        }

        if (listen(ListenSocket_fd, SVR_PORT) < 0) {
            cerr << ErrMsg("socket_init()", "listen()");
            return 1;
        }

        return 0;
    }

    int accept_request(){
        struct sockaddr_in cli_addr;
        int cli_addr_len = sizeof(cli_addr);

        int req_fd = accept(ListenSocket_fd, (struct sockaddr*)&cli_addr, (socklen_t*)&cli_addr_len);

        if (req_fd < 0) {
            if (errno == EINTR || errno == EAGAIN){ 
                // try again
                // modify later
                cerr << ErrMsg("accept_request()", "accept()", "[Need to try again]");
                return -1;
            }
            else if (errno == ENFILE) {
                cerr << ErrMsg("accept_request()", "accept()", "[Out of file descriptor table]");
                return -1; // modify later -> tell the client
            }
            else{
                cerr << ErrMsg("accept_request()", "accept()", "[Unknown]");
            }
        }

        return req_fd;
    }

    bool has_request(int timeout=WAITTIME){
        struct pollfd svr_poll;
        bzero(&svr_poll, sizeof(svr_poll));

        svr_poll.fd = ListenSocket_fd;
        svr_poll.events = POLLIN; // should not have POLLHUP

        int ret = poll(&svr_poll, 1, timeout);

        if(ret < 0){
            char msg[1024] = "";
            sprintf(msg, "errno = %d", errno);

            cerr << ErrMsg("has_request()", "poll()", msg);

            return false;
        }

        // only check whether (ret == 1);
        return (ret > 0);
    }
};

class Client{
    public:
    int sock_fd;
    FILE* sock_file;
    string name;

    Client(int fd){
        sock_fd = fd;        
        sock_file = fdopen(fd, "r+");
        name = "";
    }

    ~Client(){
        if(sock_file){
            fclose(sock_file);
        }
    }

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

    char recv_format[1024] = "";
    sprintf(recv_format, "%%%ds", MAX_NAME_LEN);
    // fscanf(clnt.sock_file, recv_format, buf_name);

    clnt.sock_fscanf(recv_format, buf_name);

    clnt.name = string(buf_name);

    cout << InfoMsg("client_func()", string("New client name = ") + clnt.name);

    // modify later
    char greeting[1024] = "";
    sprintf(greeting, "Hello from CAFE server, %s !\n", buf_name);

    clnt.sock_send(greeting);
    
    // cout << "client fprintf, " << fprintf(clnt.sock_file, "Hello from CAFE server, %s\n", buf_name) << "\n";
    // if(fflush(clnt.sock_file) < 0) cerr << ErrMsg("client_func()", "flush()");

    // cout << InfoMsg("client_func()", string("Greet written to ") + clnt.name);

    return;
}

void server_func(int* ret_ptr){
    mySocket svr_socket;

    string server("Server");
    
    cout << InfoMsg(server, "Starting...");

    if(svr_socket.socket_init()){
        *ret_ptr = 1;
        return;
    }

    char msg[1024] = "";
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