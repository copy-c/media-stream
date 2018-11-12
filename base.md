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
          
## 网络传输rtmp协议 - 传输视音频数据+播放控制信令
### 1.播放过程
1）三次握手  
2）建立网络连接  
3）建立网络流  
4）播放  
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



## 官方文档  
## 简单的example  

# webrtc交互过程  


* yuv420p, rgba内存布局
* ffmpeg工具, 官方文档, 简单的example
* rtmp协议, rtmp推流拉流
* webrtc交互过程
音视频基础知识, 视频封装和编码, 音频采样编码等概念
