#ifndef _CAMERA_GRAP_HH
#define _CAMERA_GRAP_HH
#include <linux/videodev2.h>


// projects

#include "CamConverter.hh"

#define DEFAULT_DEV_NAME "/dev/video0"
#define OUT_FILENAME     "tmp"
#define SIZE_REQ_BUFF    4
#define NAME_MAX_LENGTH  0x80
#define DF_BEBUG     1      //use to debug the program
#define FARME_MAX_SIZE 0x800

struct buffer
{
    void   *start;
    size_t  length;
};

#define CLS_VAR(x) memset(&x, 0, sizeof(x))

class CameraGrap
{
private:
    int fd;
    unsigned int n_buffers;
    struct v4l2_buffer buf;
    struct v4l2_format fmt;
    char dev_name[NAME_MAX_LENGTH];
    struct buffer  *buffers;
    char frame_name[NAME_MAX_LENGTH];
    unsigned char *frame_rgb24buffer;
    unsigned char *frame_yuv420p9buffer;

public:
    CamConverter converter;
    CameraGrap(char *dev_name, __u32 width, __u32 height);
    ~CameraGrap();

    __u32 grap_frame(const char* pic_name, int width_des, int height_des);
    __u32 get_width();
    __u32 get_height();
    unsigned char* get_yuv420p9frameBuffer();

private:
    int open_device();
    void init_device();
    void uninit_device();
    void init_mmap();
    void check_capabilities();
    int set_frame_format();
    void start_capture();
    void stop_capture();
    
    int read_frame();
    
};

#endif
/*_DF__CAMERA_H*/
