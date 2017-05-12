#ifndef _DF__CAMERA_HH
#define _DF__CAMERA_HH
#include <linux/videodev2.h>


// projects

#include "Convter.hh"

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
    /**
    __u32 format;
    __u32 width;
    __u32 height;
    **/
    unsigned int n_buffers;
    struct v4l2_buffer buf;
    struct v4l2_format fmt;
    char dev_name[NAME_MAX_LENGTH];
    struct buffer  *buffers;
    char frame_name[NAME_MAX_LENGTH];
    unsigned char *frame_buffer;

public:
    Convter convter;
    CameraGrap(char *dev_name, __u32 width, __u32 height);
    ~CameraGrap();

    __u32 grap_frame(const char* pic_name);
    //unsigned char * get_frameBuffer();
    __u32 get_width();
    __u32 get_height();
    void load_frame(AVPicture & pPictureDes, AVPixelFormat FMT, int width_des, int height_des);

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

