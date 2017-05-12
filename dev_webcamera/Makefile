
CC = g++
#CC = arm-linux-gnueabi-g++
CFLAGS = -fPIC -Wall -g -c # C flags
RM = rm -f  # rm command
LDFLAGS = -shared  # linking flags
TARGET_LIB = libcam.so # target lib
SRCS = CameraGrap.cpp Convter.cpp RtspServer.cpp # source files
OBJS = $(SRCS:.cpp=.o)

TARGET_ELF = main
# LINKFLAGS = -L./ -lcam -L./ -ljpeg
LINKFLAGS = -L/usr/lib/x86_64-linux-gnu/ -ljpeg

LIVE_LIB_PATH = ./live
LIVE_BASIC_PATH = $(LIVE_LIB_PATH)/BasicUsageEnvironment
LIVE_GROUPSOC_PATH = $(LIVE_LIB_PATH)/groupsock
LIVE_MEDIA_PATH = $(LIVE_LIB_PATH)/liveMedia
LIVE_MIDEASER_PATH = $(LIVE_LIB_PATH)/mediaServer
LIVE_PROXYSER_PATH = $(LIVE_LIB_PATH)/proxyServer
LIVE_USAGEENV_PTTH = $(LIVE_LIB_PATH)/UsageEnvironment
#LIVE_$(LIVE_LIB_PATH)/WindowsAudioInputDevice
#testProgs
LIVE_LINK = -L$(LIVE_BASIC_PATH)/ -lBasicUsageEnvironment \
			-L$(LIVE_GROUPSOC_PATH)/ -lgroupsock \
			-L$(LIVE_MEDIA_PATH)/ -lliveMedia \
			-L$(LIVE_USAGEENV_PTTH)/ -lUsageEnvironment
#			-L$(LIVE_MIDEASER_PATH)/ -l

LIVE_OBJS = $(wildcard $(LIVE_BASIC_PATH)/*.o) \
			$(wildcard $(LIVE_GROUPSOC_PATH)/*.o) \
			$(wildcard $(LIVE_MEDIA_PATH)/*.o) \
			$(wildcard $(LIVE_MIDEASER_PATH)/*.o) \
			$(wildcard $(LIVE_USAGEENV_PTTH)/*.o)
# $(wildcard $(LIVE_PROXYSER_PATH)/*.o) \

INC = -I $(LIVE_BASIC_PATH)/include \
		-I $(LIVE_GROUPSOC_PATH)/include \
		-I $(LIVE_MEDIA_PATH)/include \
		-I $(LIVE_MIDEASER_PATH)/ \
		-I $(LIVE_USAGEENV_PTTH)/include \

CFLAGS += $(INC)
LINKFLAGS += $(LIVE_LINK)

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



