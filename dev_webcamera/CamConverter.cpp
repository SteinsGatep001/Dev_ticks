#include <stdio.h>
#include <stdlib.h>
#include <jpeglib.h>
#include <errno.h>
#include <string.h>

// projects
#include "CamConverter.hh"

/**
  Print error message and terminate programm with EXIT_FAILURE return code.
  param s error message to print
*/
static void errno_exit(const char* s)
{
  fprintf(stderr, "%s error %d, %s\n", s, errno, strerror (errno));
  exit(EXIT_FAILURE);
}

void CamConverter::yuv2rgb(int width, int height, unsigned char *src, unsigned char *dst)
{
    int i, j;
    unsigned char *py, *pu, *pv;
    unsigned char *tmp = dst;

    printf("convtering width: %d height: %d\n", width, height);
    /* In this format each four bytes is two pixels. Each four bytes is two Y's, a Cb and a Cr. 
     Each Y goes to one of the pixels, and the Cb and Cr belong to both pixels. */
    py = src;
    pu = src + 1;
    pv = src + 3;

    #define CLIP(x) ( (x)>=0xFF ? 0xFF : ( (x) <= 0x00 ? 0x00 : (x) ) )

    for (i = 0; i < height; ++i)
    {
        for (j = 0; j < width; ++j)
        {
            *tmp++ = CLIP((double)*py + 1.402*((double)*pv-128.0));
            *tmp++ = CLIP((double)*py - 0.344*((double)*pu-128.0) - 0.714*((double)*pv-128.0));      
            *tmp++ = CLIP((double)*py + 1.772*((double)*pu-128.0));
            // increase py every time
            py += 2;
            // increase pu,pv every second time
            if ((j & 1)==1)
            {
                pu += 4;
                pv += 4;
            }
        }
    }
}

void CamConverter::save_jpeg(unsigned char* img, int width, int height, const char *filename, unsigned char quality)
{
    struct jpeg_compress_struct cinfo;
    struct jpeg_error_mgr jerr;

    JSAMPROW row_pointer[1];
    FILE *outfile = fopen( filename, "wb" );

    // try to open file for saving
    if (!outfile)
        errno_exit("jpeg");

    // create jpeg data
    cinfo.err = jpeg_std_error( &jerr );
    jpeg_create_compress(&cinfo);
    jpeg_stdio_dest(&cinfo, outfile);

    // set image parameters
    cinfo.image_width = width;    
    cinfo.image_height = height;
    cinfo.input_components = 3;
    cinfo.in_color_space = JCS_RGB;

    // set jpeg compression parameters to default
    jpeg_set_defaults(&cinfo);
    // and then adjust quality setting
    jpeg_set_quality(&cinfo, quality, TRUE);

    // start compress 
    jpeg_start_compress(&cinfo, TRUE);

    // feed data
    while (cinfo.next_scanline < cinfo.image_height) 
    {
        row_pointer[0] = &img[cinfo.next_scanline * cinfo.image_width *  cinfo.input_components];
        jpeg_write_scanlines(&cinfo, row_pointer, 1);
    }

    // finish compression
    jpeg_finish_compress(&cinfo);

    // destroy jpeg data
    jpeg_destroy_compress(&cinfo);

    // close output file
    fclose(outfile);
}


int CamConverter::convert_yuv2rgb(unsigned char *srcBuf, unsigned char *desBuf, struct v4l2_format *fmt, int width_des, int height_des)
{
    __u32 width = fmt->fmt.pix.width;
    __u32 height = fmt->fmt.pix.height;
    if(srcBuf == NULL || desBuf == NULL || width_des < 1 || height_des<1)
    {
        perror("error convert");
        return -1;
    }
    AVPicture pPictureSrc, pPictureDes;
    SwsContext * pSwsCtx;
    // set res yuyv
    pPictureSrc.data[0] = (unsigned char *) srcBuf;
    pPictureSrc.data[1] = pPictureSrc.data[2] = pPictureSrc.data[3] = NULL;
    pPictureSrc.linesize[0] = fmt->fmt.pix.bytesperline;
    int i = 0;
    for (i = 1; i < 8; i++)
    {
        pPictureSrc.linesize[i] = 0;
    }
    // set des
    avpicture_fill(&pPictureDes, desBuf, DF_OUT_FORMAT, width, height);
    // get PIX_FMT_YUYV422
    pSwsCtx = sws_getContext(width, height, DF_INPUT_FORMAT,\
     width_des, height_des, DF_OUT_FORMAT, \
            SWS_BICUBIC, 0, 0, 0);
    if(pSwsCtx == NULL)
    {
        perror("sws get context");
        return -1;
    }
    int res = sws_scale(pSwsCtx, pPictureSrc.data, pPictureSrc.linesize, 0, \
            height, pPictureDes.data,  pPictureDes.linesize);
    if (res == -1)
    {
        printf("Can open to change to des image");
        return -1;
    }
    sws_freeContext(pSwsCtx);
    return 0;
}
