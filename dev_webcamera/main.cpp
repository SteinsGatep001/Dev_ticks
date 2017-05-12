#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

// libc
#include <liveMedia.hh>
#include <BasicUsageEnvironment.hh>

// project
#include "CameraGrap.hh"
#include "Convter.hh"
#include "RtspCameraServer.hh"

/*
@deadfish
Testing version
*/

int main(int argc, char *argv[])
{
    int i;
    char *dev_name = NULL;
    char dev_default_name[20] = DEFAULT_DEV_NAME;
    char tmp_file_name[40] = {0};
    __u32 rd_bytes = 0;
    unsigned char *frame_buf = NULL;
    
    if(argc == 1)
    {
        dev_name = dev_default_name;
        printf("[+] Init device name default %s\n", dev_name);
    }
    else if(argc==2)
    {
        dev_name = argv[1];
    }
    printf("[+] Starting camera !\n");
    CameraGrap *ptrCamera = new CameraGrap(dev_name, 640, 480);
    for(i=0; i<10; i++)
    {
        snprintf(tmp_file_name, 40, "tmp%d.jpg", i);
        rd_bytes = ptrCamera->grap_frame(tmp_file_name);
        ptrCamera->load_frame(AVPicture & pPictureDes, V4L2_PIX_FMT_MJPEG, 640, 480);
        if (frame_buf == NULL)
        {
            /* code */
            perror("get frame buffer");
        }
        else
        {
            (ptrCamera->convter).save_jpeg(frame_buf, ptrCamera->get_width(), ptrCamera->get_height(), tmp_file_name, 70);
            printf("read %d bytes\n", rd_bytes);
        }
    }
    return 0;
}



