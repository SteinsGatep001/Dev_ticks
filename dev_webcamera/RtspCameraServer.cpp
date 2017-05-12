

#include "RtspCameraServer.hh"

RtspServer::RtspServer()
{
    scheduler = BasicTaskScheduler::createNew();
    env = BasicUsageEnvironment::createNew(*scheduler);
}


