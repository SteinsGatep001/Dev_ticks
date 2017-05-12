#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/select.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <assert.h>
#include <sys/ioctl.h>

// projects
#include "CameraGrap.hh"
#include "Convter.hh"

/**
    send request
    return -1 if error
**/
int x_ioctl(int fd, int request, void *m_arg)
{
    int ret = -1;
    do
    {
        ret = ioctl(fd, request, m_arg);
    }while(ret == -1 && EINTR == errno);/* Interrupted system call */
    return ret;
}

void x_errno_exit(const char *s)
{
    fprintf(stderr, "%s error %d, %s\n", s, errno, strerror(errno));
    exit(EXIT_FAILURE);
}

CameraGrap::CameraGrap(char *dev_name, __u32 width, __u32 height)
{
    this->fd = -1;
    this->buffers = NULL;
    memset(this->dev_name, 0, NAME_MAX_LENGTH);
    //this->format = V4L2_PIX_FMT_MJPEG;
    //this->format = V4L2_PIX_FMT_YUYV;
    
    CLS_VAR(fmt);
    this->fmt.type                = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    this->fmt.fmt.pix.width       = width;
    this->fmt.fmt.pix.height      = height;
    this->fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    this->fmt.fmt.pix.field       = V4L2_FIELD_ANY;
    snprintf(this->dev_name, NAME_MAX_LENGTH, "%s", dev_name);
    this->frame_buffer = (unsigned char *)malloc(width*height*3*sizeof(char));
    /* open and init the camera device */
    this->open_device();
    this->init_device();
    if(this->n_buffers == 0)
        x_errno_exit("[-] None spaces of buffers\n");
    this->start_capture();
}

CameraGrap::~CameraGrap()
{
    this->stop_capture();
    this->uninit_device();
    free(this->frame_buffer);
    if(close(this->fd) == -1)
        x_errno_exit("close device");
}

/**
 ** return -1 if error
**/
int CameraGrap::open_device()
{
    struct stat st;
    if(this->dev_name == NULL)
        x_errno_exit("null device name");
    
    if(stat(this->dev_name, &st) == -1)
    {
        fprintf(stderr, "[-] Cannot identify %s : %d , %s\n", this->dev_name, errno, strerror(errno));
        exit(EXIT_FAILURE);
    }
    
    this->fd = open(this->dev_name, O_RDWR /* required */ | O_NONBLOCK, 0);
    if(this->fd <= 0)
    {
        fprintf(stderr, "[-] Cannot open %s : %d , %s\n", this->dev_name, errno, strerror(errno));
        exit(EXIT_FAILURE);
    }
    else
        printf("[+] Open %s ok!\n", this->dev_name);
    return this->fd;
}

/**
    mmap frame n*buffer[v4l2_buffer.length]
    return number of buffer
**/
void CameraGrap::init_mmap()
{
    struct v4l2_requestbuffers req;
    /* Initiate Memory Mapping, User Pointer or DMA Buffer I/O. */
    CLS_VAR(req);
    req.count = SIZE_REQ_BUFF;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;
    if (x_ioctl(this->fd, VIDIOC_REQBUFS, &req) == -1)
    {
        if (EINVAL == errno)
        {
            fprintf(stderr, "%s does not support memory mapping\n", this->dev_name);
            exit(EXIT_FAILURE);
        }
        else 
            x_errno_exit("VIDIOC_REQBUFS");
    }
    /* Check size */
    if (req.count < 2)
    {
        fprintf(stderr, "Insufficient buffer memory on %s\n", this->dev_name);
        exit(EXIT_FAILURE);
    }
    buffers = (buffer*)calloc(req.count + 1, sizeof(*buffers));
    if (!buffers)
    {
        fprintf(stderr, "Out of memory\n");
        exit(EXIT_FAILURE);
    }

    for (n_buffers = 0; n_buffers < req.count; ++n_buffers)
    {
        struct v4l2_buffer buf;
        CLS_VAR(buf);
        
        //printf("Init buf %d\n", n_buffers);
        buf.type        = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory      = V4L2_MEMORY_MMAP;
        buf.index       = n_buffers;
        /* Query the status of a buffer. */
        if (x_ioctl(this->fd, VIDIOC_QUERYBUF, &buf) == -1)
            x_errno_exit("VIDIOC_QUERYBUF");
        
        buffers[n_buffers].length = buf.length;
        buffers[n_buffers].start = \
        mmap(NULL /* start anywhere */, \
              buf.length, \
              PROT_READ | PROT_WRITE /* required */, \
              MAP_SHARED /* recommended */, \
              this->fd, buf.m.offset);
        if (MAP_FAILED == buffers[n_buffers].start)
            x_errno_exit("mmap");
        #if DF_BEBUG
        printf("length: %u offset: %u\n", buf.length, buf.m.offset);
        #endif
    }
    #if DF_BEBUG
    printf("buffers size: %d\n", n_buffers);
    #endif
}

void CameraGrap::check_capabilities()
{
    struct v4l2_capability argp_cap;
    /* Query device capabilities */
    if(x_ioctl(this->fd, VIDIOC_QUERYCAP, &argp_cap) == -1)
    {
        if(EINVAL == errno)/* Invalid argument */
        {
            fprintf(stderr, "%s dose not support memory mapping\n", this->dev_name);
            exit(EXIT_FAILURE);
        }
        else
            x_errno_exit("VIDIOC_REQBUFS");
    }
    if((argp_cap.capabilities & V4L2_CAP_VIDEO_CAPTURE) == 0)
    {
        fprintf(stderr, "%s is not a video capture device\n", this->dev_name);
        exit(EXIT_FAILURE);
    }
    else
        printf("%s supports the single-planar API through the Video Capture interface.\n", this->dev_name);
}

/**
 * fd: camera fd
 * dev_name: camera name
 * vd: video information
 */
int CameraGrap::set_frame_format()
{
    unsigned char sp_flag = 0;
    struct v4l2_fmtdesc fmt_ds;
    printf("Your pixelformat = '%c%c%c%c'\n", this->format & 0xFF, (this->format >> 8) & 0xFF, (this->format >> 16) & 0xFF, (this->format >> 24) & 0xFF);
    
    CLS_VAR(fmt_ds);
    fmt_ds.index = 0;
    fmt_ds.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    while(x_ioctl(this->fd, VIDIOC_ENUM_FMT, &fmt_ds) == 0)
    {
        printf("[+] pixelformat = '%c%c%c%c', description = '%s'\n", fmt_ds.pixelformat & 0xFF, (fmt_ds.pixelformat >> 8) & 0xFF, (fmt_ds.pixelformat >> 16) & 0xFF, (fmt_ds.pixelformat >> 24) & 0xFF, fmt_ds.description);
        if(fmt_ds.pixelformat == this->format)
        {
            sp_flag = 1;
            break;
        }
        fmt_ds.index++;
    }
    if (sp_flag == 0)
        x_errno_exit("Pix format not found\n");
    else
        printf("[+] The device will use the format you have set\n");
    /* Set pix format */

    if(x_ioctl(this->fd, VIDIOC_S_FMT, &(this->fmt)) == -1)
        x_errno_exit("VIDIOC_S_FMT");
    /**
    if((fmt.fmt.pix.width != this->width) || (fmt.fmt.pix.height != this->height))
        printf("[-] The device (w:%d h:%d)\n", fmt.fmt.pix.width, fmt.fmt.pix.height);
    **/
    return 0;
}

void CameraGrap::init_device()
{
    struct v4l2_cropcap cropcap;
    struct v4l2_crop crop;
    
    this->check_capabilities();
    
    /* Check crop abilities */
    CLS_VAR(cropcap);
    cropcap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    /* Ignored some errors */
    if(x_ioctl(this->fd, VIDIOC_CROPCAP, &cropcap) == 0)
    {
        CLS_VAR(crop);
        crop.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        crop.c = cropcap.defrect;
        if(x_ioctl(this->fd, VIDIOC_S_CROP, &crop) == -1)
        {
            if(errno == EINVAL)
                printf("[-] %s does not support cropping\n", this->dev_name);
            else
                printf("[-] Other error in check cropping\n");
        }
    }
    
    this->set_frame_format();
    this->init_mmap();
}

void CameraGrap::uninit_device()
{
    unsigned int i;
    int ret = -1;
    for(i = 0; i<this->n_buffers; i++)
    {
        ret = munmap(this->buffers[i].start, this->buffers[i].length);
        if(ret == -1)
            x_errno_exit("munmap");
    }
    free(this->buffers);
}

void CameraGrap::start_capture()
{
    unsigned int i;
    enum v4l2_buf_type type;
    for(i = 0; i < this->n_buffers; i++)
    {
        struct v4l2_buffer buf;
        CLS_VAR(buf);
        buf.type   =  V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory =  V4L2_MEMORY_MMAP;
        buf.index  =  i;
        // Exchange a buffer with the driver 
        if (x_ioctl(this->fd, VIDIOC_QBUF, &buf) == -1)
            x_errno_exit("VIDIOC_QBUF");
    }
    /* Turn on the stream */
    type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if(x_ioctl(this->fd, VIDIOC_STREAMON, &type) == -1)
        x_errno_exit("VIDIOC_STREAMON");
}

void CameraGrap::stop_capture()
{
    enum v4l2_buf_type type;
    x_ioctl(this->fd, VIDIOC_STREAMOFF, &type);
    return;
}

/**
    read one frame
**/
int CameraGrap::read_frame()
{
    this->buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    this->buf.memory = V4L2_MEMORY_MMAP;
    // request to read buffer
    if(x_ioctl(this->fd, VIDIOC_DQBUF, &this->buf) == -1)
    {
        switch(errno)
        {
            case EAGAIN:
                return 0;
            default:
                x_errno_exit("VIDIOC_DQBUF");
        }
    }
    assert(this->buf.index < this->n_buffers);

    //this->save_frame();
    if(x_ioctl(this->fd, VIDIOC_QBUF, &(this->buf)) == -1)
        x_errno_exit("VIDIOC_QBUF");
    return 1;
}


__u32 CameraGrap::grap_frame(const char* frame_name)
{
    struct timeval tv;
    int ret;
    fd_set fds;
    snprintf(this->frame_name, NAME_MAX_LENGTH, "%s", frame_name);
    #if 1
    while(1)
    {
        FD_ZERO(&fds);
        FD_SET(this->fd, &fds);
        /* Set timeout */
        tv.tv_sec = 2;
        tv.tv_usec = 0;
        /* nfds is the highest-numbered file descriptor in any of the three sets, plus 1 */
        ret = select(this->fd + 1 /*nfds*/, &fds/*readfds*/, NULL/*writefds*/, NULL/*exceptfds*/, &tv);
        if(ret == 0)
        {
            fprintf(stderr, "Select timeout\n");
            exit(EXIT_FAILURE);
        }
        if(ret == -1)
        {
            if(errno == EINTR)
                continue;
        }

        if(read_frame())
            break;
    }
    #endif
    return this->buf.bytesused;
}

void CameraGrap::load_frame(AVPicture & pPictureDes, AVPixelFormat FMT, int width_des, int height_des)
{
    AVPicture pPictureSrc;
    SwsContext * pSwsCtx;
    pPictureSrc.data[0] = (unsigned char *) this->buffers[(this->buf).index].start;
    pPictureSrc.data[1] = pPictureSrc.data[2] = pPictureSrc.data[3] = NULL;
    pPictureSrc.linesize[0] = this->fmt.fmt.pix.bytesperline;
    int i = 0;
    for (i = 1; i < 8; i++)
    {
        pPictureSrc.linesize[i] = 0;
    }
    // get PIX_FMT_YUYV422 不裁剪
    pSwsCtx = sws_getContext(this->fmt.fmt.pix.width, this->fmt.fmt.pix.height, this->fmt.fmt.pix.pixelformat,\
     width_des, height_des, FMT, \
            SWS_BICUBIC, 0, 0, 0);
    int res = sws_scale(pSwsCtx, pPictureSrc.data, pPictureSrc.linesize, 0, \
            height, pPictureDes.data, pPictureDes.linesize);
    if (res == -1)
    {
        printf("Can open to change to des image");
        return false;
    }
    sws_freeContext(pSwsCtx);
    //memset(this->frame_buffer, 0, 3*(this->width)*(this->height));
    //convter.yuv2rgb(this->width, this->height, (unsigned char*)p, (unsigned char*)this->frame_buffer);
}

unsigned char * CameraGrap::get_frameBuffer()
{
    return (unsigned char*)this->frame_buffer;
}

__u32 CameraGrap::get_width()
{
    return this->fmt.fmt.pix.width;
}
__u32 CameraGrap::get_height()
{
    return this->fmt.fmt.pix.height;
}

