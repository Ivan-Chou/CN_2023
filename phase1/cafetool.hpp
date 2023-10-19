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
// for SVR_Socket.hasRequest()
#include <poll.h>

#include <cctype>
#include <iostream>
#include <vector>
#include <string>

// 0xCAFE
#define SVR_PORT 51966
// the max length of an user's name
#define MAX_NAME_LEN 15
// the max size of the buffer for send(socket, ...) and recv(socket, ...)
#define MSG_BUFMAX 1024
// the waiting time for poll()
#define WAITTIME 1000

using namespace std;

bool string2cstr(string& cpp_str, char c_str[MSG_BUFMAX]){
    if(cpp_str.length() >= MSG_BUFMAX) return false;

    bzero(c_str, (cpp_str.length() + 1) * sizeof(char));

    for(int i = 0; i < cpp_str.length(); i++){
        c_str[i] = cpp_str[i];
    }

    return true;
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

class SVR_Socket{
    public:
    int ListenSocket_fd;

    SVR_Socket(){
        ListenSocket_fd = -1;
    }

    ~SVR_Socket(){
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
            char msg[MSG_BUFMAX] = "";
            sprintf(msg, "errno = %d", errno);

            cerr << ErrMsg("has_request()", "poll()", msg);

            return false;
        }

        // only check whether (ret == 1);
        return (ret > 0);
    }
};