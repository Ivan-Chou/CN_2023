#include <sys/socket.h>
#include <unistd.h>
#include <stdio.h>
// for inet_ntoa
#include <arpa/inet.h>
// for sockaddr_in
#include <netinet/in.h>
// for bzero()
#include <string.h>
// for getaddrinfo()
#include <netdb.h>

#include <cctype>
#include <iostream>
#include <vector>
#include <string>

// 0xCAFE "+ 1"
#define CLNT_PORT 51967

using namespace std;

class CLNT_Socket{
    public:
    int sock_fd;

    CLNT_Socket(){
        sock_fd = -1;
    }

    ~CLNT_Socket(){
        if(sock_fd > 2){
            close(sock_fd);
        }
    }

    int socket_init(string serverHostName = "ws3.csie.ntu.edu.tw"){
        sock_fd = socket(AF_INET, SOCK_STREAM, 0);

        if(sock_fd < 0){
            cerr << ErrMsg("socket_init()", "socket()");
            return 1;
        }

        struct addrinfo hints, *result;

        bzero(&hints, sizeof(hints));

        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;
        hints.ai_protocol = IPPROTO_TCP;

        char buf[MSG_BUFMAX] = "";
        string2cstr(serverHostName, buf);

        if(getaddrinfo(buf, nullptr, &hints, &result) != 0){
            cerr << ErrMsg("socket_init()", "getaddrinfo()");
            return 1;
        }
        
        struct sockaddr_in servaddr;

        bzero(&servaddr, sizeof(servaddr));
        servaddr.sin_family = AF_INET;
        servaddr.sin_addr.s_addr = ((struct sockaddr_in *)result->ai_addr)->sin_addr.s_addr;
        servaddr.sin_port = htons(SVR_PORT);

        if (connect(sock_fd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0) {
            cerr << ErrMsg("socket_init()", "connect()");
            return 1;
        }

        freeaddrinfo(result);

        return 0;
    }

    ssize_t sock_recv(char* buf){
        bzero(buf, MSG_BUFMAX * sizeof(char));
        return recv(sock_fd, buf, (MSG_BUFMAX - 1) * sizeof(char), 0);
    }

    ssize_t sock_send(char* str){
        int len = strlen(str);
        ssize_t ret = send(sock_fd, str, len * sizeof(char), 0);
        if(str[len - 1] != '\n') send(sock_fd, "\n", 1, 0);
        return ret;
    }
};

class Personal_info{
    public:
    string username;
    // vector<> address_book; // people communicating with the user.

    Personal_info(string& name){
        username = name;
    }

    ~Personal_info(){}

    // modify later
};