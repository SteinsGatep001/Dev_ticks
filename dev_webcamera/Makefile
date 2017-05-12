
CC = g++
#CC = arm-linux-gnueabi-g++
CFLAGS = -fPIC -Wall -g -c # C flags
RM = rm -f  # rm command
LDFLAGS = -shared  # linking flags
TARGET_LIB = libcam.so # target lib
SRCS = CameraGrap.cpp CamConverter.cpp RtspV4l2Server.cpp # source files
OBJS = $(SRCS:.cpp=.o)
LINKFLAGS = 
INC = 

TARGET_ELF = main

BASE_LIB_PATH = ./lib

DEFAULT_LIB_PATH = /usr/local

# libjpeg
LIBJPEG_PATH = /usr/lib/x86_64-linux-gnu
LINKFLAGS += -L$(LIBJPEG_PATH)/ -ljpeg
INC += -I$(DEFAULT_LIB_PATH)/include

# complied library path
LIVE_LIB_PATH = $(BASE_LIB_PATH)/live
LIVE_BASIC_PATH = $(LIVE_LIB_PATH)/BasicUsageEnvironment
LIVE_GROUPSOC_PATH = $(LIVE_LIB_PATH)/groupsock
LIVE_MEDIA_PATH = $(LIVE_LIB_PATH)/liveMedia
LIVE_MIDEASER_PATH = $(LIVE_LIB_PATH)/mediaServer
LIVE_PROXYSER_PATH = $(LIVE_LIB_PATH)/proxyServer
LIVE_USAGEENV_PTTH = $(LIVE_LIB_PATH)/UsageEnvironment

LINKFLAGS += -L$(LIVE_BASIC_PATH)/ -lBasicUsageEnvironment \
			-L$(LIVE_GROUPSOC_PATH)/ -lgroupsock \
			-L$(LIVE_MEDIA_PATH)/ -lliveMedia \
			-L$(LIVE_USAGEENV_PTTH)/ -lUsageEnvironment

# live555 src
INC += -I $(LIVE_BASIC_PATH)/include \
		-I $(LIVE_GROUPSOC_PATH)/include \
		-I $(LIVE_MEDIA_PATH)/include \
		-I $(LIVE_MIDEASER_PATH)/ \
		-I $(LIVE_USAGEENV_PTTH)/include

# mpeg src
LINKFLAGS += -L$(DEFAULT_LIB_PATH)/lib -lavutil \
			-L$(DEFAULT_LIB_PATH)/lib -lavdevice \
			-L$(DEFAULT_LIB_PATH)/lib -lavcodec \
			-L$(DEFAULT_LIB_PATH)/lib -lavfilter \
			-L$(DEFAULT_LIB_PATH)/lib -lswscale


CFLAGS += $(INC)


#.DEFAULT_GOAL := all
#all: $(TARGET_ELF) $(TARGET_LIB)

# compile .o to .so

%.o: %.cpp
	$(CC) $(CFLAGS) $^

# compile .o to main
$(TARGET_ELF): main.o $(OBJS)
	$(CC) -o $@ $^ $(LINKFLAGS)

clean:
	$(RM) *.o libcam.so *.jpg



