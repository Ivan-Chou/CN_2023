#include <sys/socket.h>
#include <unistd.h>
#include <stdio.h>
#include <arpa/inet.h>
// for sockaddr_in
#include <netinet/in.h>
// for bzero()
#include <string.h>

#include <cctype>
#include <thread>
#include <iostream>
#include <vector>
#include <string>

// 0xCAFE
#define SVR_PORT 51966

using namespace std;

string InfoMsg(string parent, string toSay){
    return (string("<INFO> ") + parent + string(": ") + toSay + string("\n"));
}

string ErrMsg(string parent, string func, string detail = ""){
    return (string("<ERR> ") + parent + string(": ") + func + string(" failed") + (detail == "" ? string(".") : (string(", ") + detail)) + string("\n"));
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
                // continue;  // try again
                // modify later
                cerr << ErrMsg("accept_request()", "accept()", "[Need to try again]");
                return -1;
            }
            if (errno == ENFILE) {
                cerr << ErrMsg("accept_request()", "accept()", "[Out of file descriptor table]");
                return -1; // modify later -> tell the client
            }

            cerr << ErrMsg("accept_request()", "accept()", "[Unknown]");
        }

        return req_fd;
    }
};

int main(int argc, char const *argv[])
{
    mySocket svr_socket;

    string server("Server");
    
    cout << InfoMsg(server, "Starting...");

    if(svr_socket.socket_init()){
        return 1;
    }

    char msg[1024] = "";
    sprintf(msg, "Operating with socket fd = %d", svr_socket.ListenSocket_fd);

    cout << InfoMsg(server, msg);

    cout << InfoMsg(server, "Terminated.");

    return 0;
}
