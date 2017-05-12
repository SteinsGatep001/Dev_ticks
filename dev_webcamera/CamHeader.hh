#ifndef __CAM_HEADER_HH
#define __CAM_HEADER_HH

extern "C"
{
#ifdef __cplusplus

  //C99整数范围常量. [纯C程序可以不用, 而C++程序必须定义该宏.]
  #define  __STDC_LIMIT_MACROS
  //C99整数常量宏. [纯C程序可以不用, 而C++程序必须定义该宏.]
  #define  __STDC_CONSTANT_MACROS
  // for int64_t print using PRId64 format.
  #define __STDC_FORMAT_MACROS

    #ifdef _STDINT_H
      #undef _STDINT_H
    #endif

  #include <stdint.h>

#endif
}

#ifdef __cplusplus
extern "C"
{
#endif

#include "libavcodec/avcodec.h" 
#include "libavformat/avformat.h"
#include "libswscale/swscale.h"
#include "libavutil/imgutils.h"
#include "libavutil/opt.h"
#include "libavutil/mathematics.h"
#include "libavutil/pixfmt.h"
#include "libavutil/samplefmt.h"
#include <x264.h>

#ifdef __cplusplus
}
#endif


//#define DF_OUT_FORMAT AV_PIX_FMT_RGB24 
//#define DF_INPUT_FORMAT AV_PIX_FMT_YUYV422


#endif

