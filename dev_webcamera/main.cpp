#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

#include "CamHeader.hh"

// libc
#include <liveMedia.hh>
#include <BasicUsageEnvironment.hh>

// project
#include "CameraGrap.hh"
#include "CamConverter.hh"
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
    __u32 width = 640;
    __u32 height = 480;

    
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
    CameraGrap *ptrCamera = new CameraGrap(dev_name, width, height);
    for(i=0; i<10; i++)
    {
        snprintf(tmp_file_name, 40, "tmp%d.jpg", i);
        ptrCamera->grap_frame(tmp_file_name, width, height);
        frame_buf = ptrCamera->get_frameBuffer();
        if (frame_buf == NULL)
        {
            /* code */
            perror("get frame buffer");
        }
        else
        {
            //(ptrCamera->converter).save_jpeg(frame_buf, ptrCamera->get_width(), ptrCamera->get_height(), tmp_file_name, 70);
            printf("saving %s\n", tmp_file_name);
        }
    }

    free(frame_buf);
    return 0;
}



