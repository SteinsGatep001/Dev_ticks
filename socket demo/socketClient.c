#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>

#define BUF_SIZE 256
#define PORT_NUM 80

int main(int argc, char *argv[])
{
    int sock_fd = -1;//soc_fd用于获取socket返回的文件句柄
    struct sockaddr_in s_addr;
    int ret = -1;
    char buffer[BUF_SIZE] = {0};
    unsigned short portArg = 0;
    if(argc != 3)
    {
        printf("usage: %s ip port\n", argv[0]);
        exit(1);
    }
    portArg = atoi(argv[2]);
    //创建socket
    sock_fd = socket(AF_INET, SOCK_STREAM, 0);//IPV4
    if(sock_fd == -1)
    {
        printf("Create socket failed\n");
        exit(1);
    }
    printf("Socket create ok\n");
    //建立连接
    memset(&s_addr, 0, sizeof(struct sockaddr_in));
    s_addr.sin_family = AF_INET;    /* Allow IPv4 */
    s_addr.sin_port = htons(portArg); /* 端口号 */
    s_addr.sin_addr.s_addr = inet_addr(argv[1]); /* ip地址 */
    ret = connect(sock_fd, (struct sockaddr *)(&s_addr), sizeof(struct sockaddr));
    if(ret == -1)
    {
        printf("Connect fail !\r\n");
        exit(1);
    }
    printf("Connect success !\r\n");
    //等待输入
	
    while(1)
    {
        bzero(buffer,BUF_SIZE);
        fgets(buffer, BUF_SIZE - 1, stdin);
        ret = write(sock_fd, buffer, strlen(buffer));
        if(ret < 0)
        {
            printf("Send data error\n");
            break;
        }
    }
    
    return 0;
}

