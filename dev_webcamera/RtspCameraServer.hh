#ifndef _RTSPCAMERASERVER_HH
#define _RTSPCAMERASERVER_HH

class RtspServer
{
    TaskScheduler* scheduler;
    UsageEnvironment* env;
public:
    RtspServer();
    ~RtspServer();
    
};

#endif
