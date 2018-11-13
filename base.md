# 基础知识
## 内存布局  
### 1.yuv
https://blog.csdn.net/zhuweigangzwg/article/details/17222535  
1.定义：  
Y 亮度（灰度值）    
U/V 色度（指定像素颜色）  
2.优势：  
1）Y与U/V分离，没有u/v仍然能够输出图像，兼容了黑白电视  
2）不需要三路独立传输，占用带宽小  
3.yuv420p内存格式  
按yuv顺序排序，其中y是w×h个，u和v是(w/2)\*(h/2)  
比如：4 × 2  
yyyy  
yyyy  
uu  
vv  
内存则是：yyyy yyyy uu vv  
占用的内存：w*h*3/2  
4.420采样规律  
一组U/V被4个Y使用  
奇数行采样：采样y，采样1/2 u，不采样v  
偶数行采样：采样y，采样1/2 v，不采样u  
5.  
480P 逐行
480I 隔行
### 2.rgba  
          
## 网络传输rtmp协议
### 1.交互过程
握手 + 控制播放信令 + 传输音视数据  
### 2.推流与拉流
推流：摄像机将码流推向源站  
拉流：播放器向CDN节点拉流，CDN向源站拉流  
https://cloud.tencent.com/developer/article/1004970 重点再看

## 总结
1）解协议 RTMP 去除控制信令等 -> FLV格式数据  
2）解封装(.mkv) -> H.264（压缩标准）视频码流 + ACC音频码流  
3）解码（将压缩数据解码成非压缩数据）-> 产生原始数据YUV 
4）转换 根据YUV420P采样恢复每个像素的YUV值 -> 根据YUV2RGB公式恢复 -> 每个像素的RGB  
  
# ffmpeg  
https://blog.csdn.net/leixiaohua1020/article/details/15811977  
## 使用
1.编码 YUV -> H.264 encode   
libavcodec  
2.解码 H.264 -> YUV decode    
## 常用数据结构
https://blog.csdn.net/leixiaohua1020/article/details/11693997  
1.解协议（http、rtsp）  
```c
AVIOContext、URLContext、URLProtocol 存储视音频使用的协议类型及状态
AVIOContext
{
    // 管理输入输出数据的结构体
    // 核心
    unsigned char *buffer; // 缓存开始位置
    // buffer 用于存储ffmpeg读入的数据，当打开一个视频文件时，先把数据从硬盘读入buffer，然后再送去解码
    unsigned char *buf_ptr; // 当前指针读取到的位置
    unsigned char *buf_end; // 缓存结束的位置
    int buffer_size; // 缓存大小
    void *opaque; // URLContext结构体
}

URLContext
{
    const AVClass *av_class; // information for av_log()
    struct URLProtocol *prot; // URLProtocal 
    char *filename; // specified URL
}

URLProtocol
{
    const char *name; // rtmp http
    int (*url_open);
    int (*url_read);
    int (*url_write);
    int (*url_close);
    struct URLProtocal *next;
}
```
2.解封装（flv、mkv）  
```c
AVFormatContext 存储视音频封装格式中包含的信息
AVInputFormat 存储输入视音频使用的封装格式
AVFormatContext
{
    struct AVInputFormat *iformat; // 输入数据的封装格式
    struct AVOutputFormat *oformat; // 输入数据的封装格式

    AVIOContext *pb; // 输入数据的缓存
    unsigned int nb_streams; // 视音频流的个数
    AVStream **streams; // 视音频流
    char filename[1024] // 文件名
    int64_t duration; // 视频时长 us
    int bit_rate; // 比特率 bps
    AVDictionary ×metadata; // 元数据
}
``` 
3.解码（h264、mpeg2、aac、mp3）  
```c
AVStream 存储一个视频、音频流相关数据，每个AVStream对应一个AVCodecContext
AVCodecContext 存储该视频、音频流使用的解码方式的相关数据，每个AVCodecContext中对应一个AVCodec
AVCodec 该视频、音频对应的解码器

AVStream
{
    // 存储每一个视频、音频流信息的结构体
    int index; // stream index in AVFormatContext 标识该音频、视频流
    int id; // format-specific stream ID
    AVCodecContext *codec; // codec context 指向该视频、音频流的AVCodecContext
    AVRational time_base; // 时基 通过该值可以把PTS、DTS转化为真正的时间
    int64_t duration; // 该视频、音频流长度
    AVDictionary *metadata; // 元数据信息 ×××
    AVRational avg_frame_rate; // 帧率
    AVPacket attached_pic; // 附带的图片
}

AVCodecContext
{
    enum AVMediaType codec_type; // 编解码器的类型
    strcut AVCodec *codec; // 采用的解码器
    int bit_rate; // 平均比特率
    uint8_t *extradata;
    int extradata_size; // 针对特定编码器包含的附加信息
    AVRational time_base; // 根据该参数，可以把PTS转换为实际的时间
    int width, height; // 视频的宽、高
    int rets; // 运动估计参考帧的个数
    int sample_rate; // 采样率
    int channels; // 声道数
    enum AVSampleFormat sample_fmt; // 采样格式
    int profile; // 型
    int level; // 级
}

AVCodec // 存储编解码器信息
{
    const char *name; // 编解码器的名字，短
    const char *long_name; // 编解码器的名字，全称
    enum AVMediaType type; // 类型，视频、音频、字幕
    enum AVCodecID id; // AV_CODEC_ID_H264等等
    const enum AVPixelFormat *pix_fmts; // 支持的像素格式 AV_PIX_FMT_YUV420P
    // 注册
    // 遍历
    av_register_all() // 全部注册
    av_codec_next() // 获取下一个编码器的指针
}
```

4.存数据  
```c
视频：每个结构存一帧
音频：每个结构可以存好几帧
AVPacket 解码前的数据 
AVFrame 解码后的数据

AVPacket
{
    uint8_t *data; // 压缩编码的数据
    int size; // data的大小
    int64_t pts; // 显示时间戳
    int64_t dts; // 解码时间戳
    int stream_index; // 标识该AVPacket所属的视频、音频流
}

AVFrame
{
    // 一般存储原始数据，即非压缩数据，例如对视频来说的YUV、RGB，音频的PCM
    // 此外还存储了宏块类型表，QP表，运动矢量表等数据
    uint8_t *data[AV_NUM_DATA_POINTERS]; // 解码后原始数据 
    // planar格式数据
    // data[0]存Y，data[1]存U，data[2]存V 
    int linesize[AV_NUM_DATA_POINTERS]; // data中一行的数据大小，未必等于图像的宽
    int width, height; // 视频帧的宽与高
    int nb_samples; // 音频的一个AVFrame中可能包含多个音频帧
    int format; // 解码后原始数据类型（YUV420）
    int key_frame; // 是否为关键帧
    enum AVPictureType pict_type; // 帧类型
    AVRational sample_aspect_ratio; // 宽高比
    int64_t pts; // 显示时间戳
    int coded_picture_number; // 编码帧序号
    int display_picture_number; // 显示帧序号
    int8_t *qscale_table; // QP表
    uint8_t *mbskip_table; // 跳过宏块表
    int16_t (*motion_val[2])[2]; // 运动矢量表
    uint32_t *mb_type; // 宏块类型表
    short *dct_coeff; // DCT系数 
    int8_t *ref_index[2]; // 运动估计参数帧列表
    int interlaced_frame; // 是否隔行扫描
    uint8_t motion_subsample_log2; // 一个宏块中的运动矢量采样个数，取log
}
```

## 官方文档  
https://github.com/FFmpeg/FFmpeg/tree/master/doc

## 简单的example  
https://blog.csdn.net/leixiaohua1020/article/details/8652605


# webrtc交互过程  
## 交互

## API
https://developer.mozilla.org/zh-CN/docs/Web/API/WebRTC_API

音视频基础知识, 视频封装和编码, 音频采样编码等概念
