#ifndef SERVER_HPP
#define SERVER_HPP

#include "basic_header.hpp"

class Server {
  private:
    int server_fd;
    int status;
    struct addrinfo host_info;
    struct addrinfo *host_info_list;

    // might not need
    struct sockaddr_storage sockets_addr;
    socklen_t sockets_addr_len;


};

#endif