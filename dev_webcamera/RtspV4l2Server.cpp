

#include "RtspV4l2Server.hh"

RtspV4l2Server::RtspV4l2Server()
{
    this->scheduler = BasicTaskScheduler::createNew();
    this->env = BasicUsageEnvironment::createNew(*scheduler);
    authDB = NULL;
    rtspServer =  RTSPServer::createNew(*(this->env), 8554, authDB);
    if (rtspServer == NULL)
    {
        /* code */
        *env << "Failed to create RTSP server: " << env->getResultMsg() << "\n";  
        exit(1);  
    }
}


