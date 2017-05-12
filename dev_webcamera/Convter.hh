



#ifndef _CONVTER_HH
#define _CONVTER_HH

#include <linux/videodev2.h>

class Convter
{
public:
    void yuv2rgb(int width, int height, unsigned char *src, unsigned char *dst);
    void save_jpeg(unsigned char* img, int width, int height, char *filename, unsigned char quality);
};

#endif
