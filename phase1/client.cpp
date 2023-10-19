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
#include <thread>
#include <iostream>
#include <vector>
#include <string>

using namespace std;

#include "cafetool.hpp"
#include "clienttool.hpp"

const vector<string> reservedUsername = {"Server"};

string getValidUsername();

bool string2cstr(string&, char[MSG_BUFMAX]);

int main(int argc, char** argv){
    CLNT_Socket ToServer;

    if(ToServer.socket_init()){
        return 1;
    }

    string name = getValidUsername();

    Personal_info user_info(name);

    char buf[MSG_BUFMAX] = "";

    string2cstr(user_info.username, buf);

    ToServer.sock_send(buf);

    ToServer.sock_recv(buf);

    cout << "[Server] " << buf << "\n";

    return 0;
}

bool ValidUsername(string& username){
    // length validity
    if(username.length() <= 0 && username.length() > 15){
        cout << "Invalid username: Length of username doesn't in [0~15].\nPlease use another name.\n";
        return false;
    }

    // check whether the name is reserved
    for(auto& name : reservedUsername){
        if(username == name){
            cout << "Invalid username: Sorry, name \"" << username << "\" is a reserved name.\nPlease use another name.\n";
            return false;
        }
    }

    // check online users -> server command?

    // check each char
    for(auto c : username){
        if(!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') && !(c >= '0' && c <= '9') && !(c == '_')){
            cout << "Invalid username: Contains invalid character \'" << c << "\'\nPlease use another name.\n";
            return false;
        }
    }

    return true;
}

string getValidUsername(){
    string username = "";

    do{
        cout << "Please enter your username on CAFE (note: <= " << MAX_NAME_LEN << " characters, only contains [A~Z, a~z, 0~9, _]):\n";
        cin >> username;
    }while(!ValidUsername(username));

    return username;
}