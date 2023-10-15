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
// 0xCAFE "+ 1"
#define CLNT_PORT 51967

