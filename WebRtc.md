# 
## 架构与服务
### 架构
web api
voice engine
video engine
session
### 服务
#### 1.信令（web与web服务器）
1）功能
a.协商媒体功能和设置
b.标识和验证会话参与者的身份
c.控制媒体的进度
2）方法
第一种：双方交换Session Description对象 -> 了解某一方支持什么格式以及将要发什么格式、某一方建立点对点通讯的网络信息
第二种：可以用任何消息机制和消息协议来进行交换
#### 2.媒体数据（web与web之间）

## 建立会话流程
### 1.获取本地媒体
getUserMedia() // 单个本地流，可使用MediaStream() API整合  
### 2.建立对等连接
每个端之间都需要一个连接  
创建新的RTCPeerConnection对象  
### 3.交换信令或媒体数据
建立连接后，可将任意数量的本地媒体流关联到对等连接，以通过该连接发送至远端浏览器  
两个浏览器交换RTCSessionDescription对象，即可建立媒体或者数据会话 -> 打洞 -> 协商秘钥 -> 媒体会话  
### 4.关闭
RTCPeerConnection调用close()来指示连接已使用完毕  
若一端奔溃，另一端会尝试重新打洞，有一个长连接  
### 总结
其中的交互/认证都是通过共同的web服务器完成，浏览器之间相互打洞（确定最佳访问方式），音视频的流直接通过浏览器完成  

## 相关API
### 1.功能划分
1.获取音频和视频数据
2.传输音频和视频数据
3.传输任意二进制数据
### 2.API划分 （js接口）
1.MediaStream (又叫getUserMedia)
1）抽象表示一个音频或者视频流
2）可包含多个音视频记录
3）js通过getUserMedia()获取
2.RTCPeerConnection (C++)
1）信令处理
2）编解码协商
3）点对点传输
4）通讯安全保护
5）带宽管理（手机上调低，pc上调高）
3.RTCDataChannel
使得浏览器之间（点对点）建立一个高吞吐量、低延时的信道，用于传输任意数据  

## 其他概念
### 打洞服务器（防火墙穿越服务器）
#### 1.方法
1）有防火墙和地址转换的p2p需要UDP打洞（只有udp可以打洞）
2）STUN/TURN/ICE服务

## 源码分析
1.api  
接口层，包括DataChannel、MediaStream、SDP相关接口  
各浏览器都通过该接口层调用webRTC  
2.call  
webRCT中call相关逻辑层代码
3.audio
存放音频网络逻辑层相关代码，音频逻辑上的发送，接收等
4.video   
存放视频逻辑层及视频引擎层相关代码，视频逻辑上发送，接收等  
5.sdk  
存放Android、IOS层代码，如视频的采集，渲染代码  
6.pc  
存放业务逻辑代码，channel，session等  
7.common_audio  
音频基本算法，环形队列、傅里叶算法、滤波器等  
8.common_video  
视频基本工具，libyuv、sps/pps分析器、l420缓冲器等  
9.modules  
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
10.media  
存放媒体相关  
11.p2p  
p2p相关  
12.rtc_base  
基础代码  
13.rtc_tools   
工具代码  
14.stats  
数据统计相关  
15.system_wrapper   
操作系统相关 
