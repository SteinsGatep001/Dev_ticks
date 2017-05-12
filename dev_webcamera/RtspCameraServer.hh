#ifndef _RTSPCAMERASERVER_HH
#define _RTSPCAMERASERVER_HH

#include "liveMedia.hh"
#include "BasicUsageEnvironment.hh"

class RtspServer
{
    TaskScheduler* scheduler;
    UsageEnvironment* env;
public:
    RtspServer();
    ~RtspServer();
    
};

#endif
