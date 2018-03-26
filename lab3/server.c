// CS164 Lab3 by Hanzhe Teng on 1/25/2018
// Socket Server C Program

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>

int main(void)
{
  int listenfd = 0,connfd = 0, n=0;
  char sendBuff[1025];
  char recvBuff[1024];
  struct sockaddr_in serv_addr;
  memset(&serv_addr, '0', sizeof(serv_addr));
  memset(sendBuff, '0', sizeof(sendBuff));
  memset(recvBuff, '0', sizeof(sendBuff));

  //int socket(int domain, int type, int protocol);
  listenfd = socket(AF_INET, SOCK_STREAM, 0);  // IPv4, TCP, auto choose protocol
  printf("socket retrieve success\n");

  serv_addr.sin_family = AF_INET;
  serv_addr.sin_addr.s_addr = htonl(INADDR_ANY); // server bind to all interfaces
  serv_addr.sin_port = htons(5000);

  bind(listenfd, (struct sockaddr*)&serv_addr,sizeof(serv_addr));

  if(listen(listenfd, 10) == -1){   // queue:10
      printf("Failed to listen\n");
      return -1;
  }

  while(1)
    {
      connfd = accept(listenfd, (struct sockaddr*)NULL ,NULL); // accept awaiting request

      pid_t pid = fork();
      if(pid == 0)
      {
        while(n = read(connfd, recvBuff, sizeof(recvBuff)-1))
        {
          recvBuff[n] = 0;
          fputs(recvBuff, stdout);
          sleep(1);
        }
        exit(0);
      }
      else
      {
        strcpy(sendBuff, "Hello from server\n");
        write(connfd, sendBuff, strlen(sendBuff));
        while(fgets(sendBuff,1023,stdin) != NULL)
        {
          write(connfd, sendBuff, strlen(sendBuff));
        }
      }

      close(connfd);
    }

  return 0;
}

