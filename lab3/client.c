// CS164 Lab3 by Hanzhe Teng on 1/25/2018
// Socket Client C Program

#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>
 
int main(int argc, char* argv[])
{
  int sockfd = 0,n = 0;
  char recvBuff[1024];
  char sendBuff[1025];
  struct sockaddr_in serv_addr;
  struct hostent *hostname;
  memset(recvBuff, '0' ,sizeof(recvBuff));
  memset(sendBuff, '0' ,sizeof(sendBuff));

  if((sockfd = socket(AF_INET, SOCK_STREAM, 0))< 0)
  {
    printf("\n Error : Could not create socket \n");
    return 1;
  }

  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(5000);

  if(argc<2)
  {
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  }
  else
  {
    hostname = gethostbyname(argv[1]);
    if(hostname == NULL)
    {
      fprintf(stdout,"Host not found \n");
      exit(1);
    }
    bcopy((char *)hostname->h_addr,(char *)&serv_addr.sin_addr.s_addr,hostname->h_length);
  }

  if(connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr))<0)
  {
    printf("\n Error : Connect Failed \n");
    return 1;
  }

  pid_t pid = fork();
  if(pid == 0)
  {
    while(n = read(sockfd, recvBuff, sizeof(recvBuff)-1))
    {
      recvBuff[n] = 0;
      fputs(recvBuff, stdout);
      sleep(1);
    }
    exit(0);
  }
  else
  {
    strcpy(sendBuff, "Hello from client\n");
    write(sockfd, sendBuff, strlen(sendBuff));
    while(fgets(sendBuff,1023,stdin) != NULL)
    {
      write(sockfd, sendBuff, strlen(sendBuff));
    }
  }

  return 0;
}

