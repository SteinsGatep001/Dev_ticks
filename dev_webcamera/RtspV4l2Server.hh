#ifndef _RTSP_V4L2_SERVER_HH
#define _RTSP_V4L2_SERVER_HH

#include "liveMedia.hh"
#include "BasicUsageEnvironment.hh"

class RtspV4l2Server
{
public:
    TaskScheduler* scheduler;
    UsageEnvironment* env;
    UserAuthenticationDatabase* authDB;
    RTSPServer* rtspServer;

    RtspV4l2Server();
    ~RtspV4l2Server();
    
};

#endif
