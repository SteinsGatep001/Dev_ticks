#ifndef _CAM_CONVERTER_HH
#define _CAM_CONVERTER_HH

#include <linux/videodev2.h>

// library extend
#include "CamHeader.hh"

class CamConverter
{
    AVPicture pictureDes;
public:
    void yuv2rgb(int width, int height, unsigned char *src, unsigned char *dst);
    void save_jpeg(unsigned char* img, int width, int height, const char *filename, unsigned char quality);
    int convert_yuyv2rgb24(unsigned char *srcBuf, unsigned char *desBuf, struct v4l2_format *fmt, int width_des, int height_des);
    int convert_src2des(unsigned char *srcBuf, unsigned char *desBuf, int width, int height, int width_des, int height_des, AVPixelFormat resFMT, AVPixelFormat desFMT);
    int encode_h264(unsigned char *srcBuf);

};

#endif
