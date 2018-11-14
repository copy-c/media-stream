## 源码分析
### api  
接口层，包括DataChannel、MediaStream、SDP相关接口  
各浏览器都通过该接口层调用webRTC  
### audio
存放音频网络逻辑层相关代码，音频逻辑上的发送，接收等
### call  
webRCT中call相关逻辑层代码
### common_audio  
音频基本算法，环形队列、傅里叶算法、滤波器等  
### common_video  
视频基本工具，libyuv、sps/pps分析器、l420缓冲器等  
### media  
存放媒体相关  
### modules  
重要！ 音视频的采集、处理、编解码器、混音等  
--
    -- audio_coding ： 音频编解码相关
    -- audio_conference_mixer ： 会议混音
    -- audio_device ： 音频采集与音频播放
    -- audio_mixer ： 混音相关
    -- audio_mixer : 混音相关代码，这部分是后加的
    -- audio_processing : 音频前后处理的相关代码
    
    -- video_capture : 视频采集相关的代码
    -- video_coding : 视频编解码相关的代码
    -- video_processing : 视频前后处理相关的代码
    -- video_capture 视频采集相关的代码

    -- bitrate_controller : 码率控制相关代码
    -- congestion_controller : 流控相关的代码
    -- pacing : 码率探测相关的代码
    -- remote_bitrate_estimator : 远端码率估算相关的--代码

    -- desktop_capture : 桌面采集相关的代码
    -- media_file : 播放媒体文件相关的代码
    -- rtp_rtcp : rtp/rtcp协议相关代码
### p2p  
p2p相关  
### pc  
存放业务逻辑代码，channel，session等  
### rtc_base  
基础代码  
### rtc_tools   
工具代码  
### sdk  
存放Android、IOS层代码，如视频的采集，渲染代码  
### stats  
数据统计相关  
### system_wrapper   
操作系统相关  
### video   
存放视频逻辑层及视频引擎层相关代码，视频逻辑上发送，接收等  
