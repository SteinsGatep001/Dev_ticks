#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <netdb.h>

#define BUF_SIZE 4096
#define PORT_NUM 80
#define IP_LENTH 15
// 169.254.188.30

#define PAGE "/"  
#define PORT 80

int sock_connect(char *sock_ip, unsigned short port);
int get_postStr(char str_post[2048], char *host, char *page);
void get_ip(char *host, char *ip);

int main(int argc, char *argv[])
{
    int sock_fd = -1;//soc_fd用于获取socket返回的文件句柄
    int ret = -1;
    char response[BUF_SIZE] = {0};
    unsigned short portArg = 0;
    struct hostent *host;
    char sock_ip[IP_LENTH+1] = {0};
    int bytes = 0;
    int total = 0;

    if(argc < 4)
    {
        printf("usage: ./%s server port page\n", argv[0]);
        exit(1);
    }
    //建立连接
    get_ip(argv[1], sock_ip);
    portArg = atoi(argv[2]);
    printf("Ip: %s\nPort: %d\n", sock_ip, portArg);
    sock_fd = sock_connect(sock_ip, portArg);
    printf("get sock_fd : %d\n", sock_fd);
    //获得post包头
    char str_post[2048] = {0};
    get_postStr(str_post, argv[1], argv[3]);
    //发送请求
    ret = send(sock_fd , str_post, strlen(str_post), 0);
    if(ret == -1)
    {
        printf("向服务器发送请求的request失败!\n");
        exit(1);
    }
    total = strlen(str_post);
    printf("Send %d bytes ok\n", total);
    printf("-------------------------------------------\n");
    printf("%s", str_post);
    //接受回应
    printf("Start receving\n");
    memset(response,0,sizeof(response));
    ret = recv(sock_fd, response, BUF_SIZE, 0);
    printf("Get %d bytes data\n", ret);
    printf("--------------------------------\n");
    printf("%s", response);
    //关闭socket
    close(sock_fd);
    return 0;
}

/* 连接
    sock_ip : ip地址
    port : 端口号
*/
int sock_connect(char *sock_ip, unsigned short port)
{
    struct sockaddr_in s_addr;
    //创建socket
    int sock_fd = socket(AF_INET, SOCK_STREAM, 0);//IPV4
    if(sock_fd == -1)
    {
        printf("Create socket failed\n");
        exit(1);
    }
    printf("Socket create ok\n");
    //建立连接
    memset(&s_addr, 0, sizeof(struct sockaddr_in));
    s_addr.sin_family = AF_INET;    /* Allow IPv4 */
    s_addr.sin_port = htons(port); /* 端口号 */
    s_addr.sin_addr.s_addr = inet_addr(sock_ip); /* ip地址 */
    int ret = connect(sock_fd, (struct sockaddr *)(&s_addr), sizeof(struct sockaddr));
    if(ret == -1)
    {
        printf("Connect failed!\r\n");
        exit(1);
    }
    printf("Connect success !\r\n");
    return sock_fd;
}

/*
    str_post : post包
    host : 服务器域名
    page : 申请的页面
*/
int get_postStr(char str_post[2048], char *host, char *page)
{
    //构建post请求
    char str_s[2048] = {0};
    memset(str_s, 0, sizeof(str_s));
    sprintf(str_s,"GET %s HTTP/1.1\r\n", page);
    strcat(str_s,"Accept: text/html, image/jpeg, image/png, vedio/x-mng, text/*, image/*, */*\r\n");
    strcat(str_s,"Accept-Lauguage: zh-cn\r\n");
    strcat(str_s,"Accept-Encoding: x-gzip, x-deflate, gzip, deflat\r\n");
    strcat(str_s,"Accept-charset: utf-8, utf-8; q=0.5, *; q=0.5\r\n");
    strcat(str_s,"HOST: ");
    strcat(str_s,host);
    strcat(str_s,"\r\n");
    strcat(str_s,"Connection: Keep-Alive\r\n");
    strcat(str_s,"Cache-Control: no-cache\r\n\r\n");
    memset(str_post, 0, sizeof(str_post));
    strcat(str_post, str_s);
    return 0;
}

/**
    host : 域名
    ip : ip地址
**/
void get_ip(char *host, char *ip)
{  
    struct hostent *hent;
    int ip_len = IP_LENTH;
    if((hent=gethostbyname(host))==NULL)
    {  
        perror("Can't get ip");  
        exit(1);  
    }  
    if(inet_ntop(AF_INET,(void *)hent->h_addr_list[0],ip,ip_len)==NULL)
    {
        perror("Can't resolve host!");
        exit(1);
    }
} 

