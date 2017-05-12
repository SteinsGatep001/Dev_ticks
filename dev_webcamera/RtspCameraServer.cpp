#include "liveMedia.hh"
#include "BasicUsageEnvironment.hh"

RtspServer::RtspServer()
{
    scheduler = BasicTaskScheduler::createNew();
    env = BasicUsageEnvironment::createNew(*scheduler);
}


