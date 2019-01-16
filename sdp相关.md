# 码率相关
## 示例
```c++
m=video 9 UDP/TLS/RTP/SAVPF 100  
b=AS:20  
a=fmtp:100 x-google-max-bitrate=30;x-google-min-bitrate=20;x-google-start-bitrate=25
```
## 规则
1.b 
  >AS 应用的最大带宽  
  >必须要在m=video组内，否则不能生效  
  >设置最大的带宽，且优先级高于x-google-max-bitrate  

2.x-google 
  >a=fmtp:xx 子属性 xx号要绑定相应的编码器  
  >x-google-max-bitrate:视频码流最大值，当网络特别好时，码流最大能达到这个值，如果不设置这个值，网络好时码流会非常大   
  >x-google-min-bitrate:视频码流最小值，当网络不太好时，WebRTC的码流每次5%递减，直到这个最小值为，如果没有设置这个值，网络不好时，视频质量会非常差   
  >x-google-start-bitrate:视频编码初始值，当网络好时，码流会向最大值递增，当网络差时，码流会向最小值递减。

## 源码分析
### 1.解析保存sdp
```c++
SessionDescriptionInterface *OfferSdp(CreateSessionDescription())
  ||
CreateSessionDescription // jsepsessiondescription.cc
  ||
SdpDeserialize(sdp, jsep_desc.get(), error_out) // webrtcsdp.cc
{
  ParseSessionDescription
  ParseMediaDescription
  {
    // 1.1 找到m=video
      while (!IsLineType(message, kLineTypeMedia, *pos)) 
    // 1.2 循环解析m=video之后的属性
      // 1.2.1 找到b=AS:
      IsLineType(line, kLineTypeSessionBandwidth)
      {
        media_desc->set_bandwidth(b * 1000); // b 单位 kbps -> bps
      }
      // 1.2.2 解析fmtp，并以(name, value)形式存储在video.codec中
  }
}
```
### 2.设置码率
```c++
PeerConn_->SetRemoteDescription(description_)
    ||
UpdateSessionState
{
  VideoChannel::SetLocalContent_w
  media_channel()->SetSendParameters(recv_params)
  {
    WebRtcVideoChannel::SetSendParameters // webrtcvideoengine.cc
    {
      // 从video.codec中获取设置的max_bitrate、min_bitrate、start_bitrate码率
      bitrate_config_ = GetBitrateConfigForCodec(send_codec_->codec);
      // b=AS: 若没有设置，则max_bandwidth_bps = -1，此时max_bitrate不变；若max_bandwidth_bps > 0, 则max_bitrate=max_bandwidth_bps；
      // 即 b=AS: 优先级高于 x-google-min-bitrate
      call_->GetTransportControllerSend()->SetSdpBitrateParameters(
        bitrate_config_);
    }
  }
}
    ||
RtpTransportControllerSend::SetSdpBitrateParameters
    ||
SendSideCongestionController::SetBweBitrates
{
  bitrate_controller_->SetBitrates(start_bitrate_bps, min_bitrate_bps, max_bitrate_bps)
}
```
### 3.使用码率：网络反馈、编码器使用
```c++
SendSideCongestionController::MaybeTriggerOnNetworkChanged
    ||
Call::OnNetworkChanged 
    ||
BitrateAllocator::OnNetworkChanged
    ||
VideoSendStreamImpl::OnBitrateUpdated
    ||
FecController::UpdateFecRates and CalculateOverheadRateBps
    ||
VideoStreamEncoder::OnBitrateUpdated
    ||
VideoSender::SetChannelParameters
    ||
VCMGenericEncoder::SetEncoderParameters
    ||
VideoEncoder::SetRateAllocation
```
# 码流相关
## 示例
a=fmtp:100 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42001f
## 规则
  >packetization-mode:表示载荷类型（0：单一NAL  1：非交错  2：交错，隔行扫描）  
  >profile-level-id:前两位来区分BP还是HP，64表示HP，42表示BP。后两位表示level-id，每个level-id对应不同的分辨率。

# rtp/rtcp相关
## 示例
```c++
a=rtcp-fb:100 goog-remb  
a=rtcp-fb:100 transport-cc  
a=rtcp-fb:100 ccm fir
a=rtcp-fb:100 nack
a=rtcp-fb:100 nack pli
```
## 规则
> goog-remb:接收端最大接收码率估测，接收端会估计本地接收的最大带宽能力，并通过rtcp remb消息返回给对端，进而调整发送端码率，达到动态调整带宽得目的;
> transport-cc:支持使用rtcp来控制拥塞
> ccm fir:支持使用rtcp反馈机制来实现编码控制，并支持fir请求
> nack:支持重传
> nack pli:支持pil请求

## 源码分析
### 1.解析保存
同码率解析
### 2.使用参数
```c++
WebRtcVideoChannel
{
  AddRecvStream
  {
    ConfigureReceiverRtp(&config, &flexfec_config) 
    {
      // 通过codec更新rtp/rtcp的设置
    }  
    receive_stream_ = new WebRtcVideoReceiveStream(config, recv_codecs_);
    {
      RecreateWebRtcVideoStream
      {
        stream_ = call_->CreateVideoReceiveStream(std::move(config));
        {
          VideoReceiveStream* receive_stream = new VideoReceiveStream(configuration)
          {
            // 用到rtp的配置 rtcp-fb 赋值位config_
            rtp_video_stream_receiver_(config_)
            RtpVideoStreamReceiver::RtpVideoStreamReceiver
            {
              config.rtp =
              HasTransportCc()
            }
          }
        }
      }
    }
  }
}
```

# 源码中记录的字段
```c++
  // H264相关 fmtp
  kH264FmtpProfileLevelId = "profile-level-id";
  kH264FmtpLevelAsymmetryAllowed = "level-asymmetry-allowed";
  kH264FmtpPacketizationMode = "packetization-mode";
  kH264FmtpSpropParameterSets = "sprop-parameter-sets";
  kH264ProfileLevelConstrainedBaseline = "42e01f";

  // 码率控制相关 fmtp
  kCodecParamMaxBitrate = "x-google-max-bitrate";
  kCodecParamMinBitrate = "x-google-min-bitrate";
  kCodecParamStartBitrate = "x-google-start-bitrate";
  kCodecParamMaxQuantization = "x-google-max-quantization";
  kCodecParamPort = "x-google-port";

  // a=
  kCodecParamPTime = "ptime"; // packet time
  kCodecParamMaxPTime = "maxptime"; // maximum packet time

  // opus 音频相关参数 fmtp
  kCodecParamMinPTime = "minptime"; // 最小帧时间
  kCodecParamSPropStereo = "sprop-stereo";
  kCodecParamStereo = "stereo";
  kCodecParamUseInbandFec = "useinbandfec"; // 使用opus编码内置fec特性
  kCodecParamUseDtx = "usedtx";
  kCodecParamMaxAverageBitrate = "maxaveragebitrate"; //最大音频码率
  kCodecParamMaxPlaybackRate = "maxplaybackrate"; // 最大采样率

  // rtcp-feedback rtcp-fb
  kRtcpFbParamNack = "nack"; 
  kRtcpFbNackParamPli = "pli";
  kRtcpFbParamRemb = "goog-remb";
  kRtcpFbParamTransportCc = "transport-cc"; // 支持使用rtcp来控制拥塞
  kRtcpFbParamCcm = "ccm";
  kRtcpFbCcmParamFir = "fir";
```

# 参考
1.SDP协议
https://tools.ietf.org/html/rfc4566#section-6  

# 附 SDP完整请求
## 七牛
```c++
v=0
o=- 5672891539379490860 2 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE audio video
a=msid-semantic: WMS
m=audio 9 UDP/TLS/RTP/SAVPF 111 103 104 9 0 8 106 105 13 110 112 113 126
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:1DdQ
a=ice-pwd:z7fuTUBTI9Zr/JksPfPqBUTz
a=ice-options:trickle
a=fingerprint:sha-256 CA:E3:B5:D7:01:F7:2A:27:F7:90:64:4F:D8:06:DE:3D:44:EA:BE:D9:B5:45:12:63:55:9E:9A:99:9D:CF:4D:FA
a=setup:actpass
a=mid:audio
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=recvonly
a=rtcp-mux
a=rtpmap:111 opus/48000/2
a=rtcp-fb:111 transport-cc
a=fmtp:111 minptime=10;useinbandfec=1
a=rtpmap:103 ISAC/16000
a=rtpmap:104 ISAC/32000
a=rtpmap:9 G722/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:106 CN/32000
a=rtpmap:105 CN/16000
a=rtpmap:13 CN/8000
a=rtpmap:110 telephone-event/48000
a=rtpmap:112 telephone-event/32000
a=rtpmap:113 telephone-event/16000
a=rtpmap:126 telephone-event/8000
m=video 9 UDP/TLS/RTP/SAVPF 96 97 98 99 100 101 102 123 127 122 125 107 108 109 124
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:1DdQ
a=ice-pwd:z7fuTUBTI9Zr/JksPfPqBUTz
a=ice-options:trickle
a=fingerprint:sha-256 CA:E3:B5:D7:01:F7:2A:27:F7:90:64:4F:D8:06:DE:3D:44:EA:BE:D9:B5:45:12:63:55:9E:9A:99:9D:CF:4D:FA
a=setup:actpass
a=mid:video
a=extmap:2 urn:ietf:params:rtp-hdrext:toffset
a=extmap:3 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time
a=extmap:4 urn:3gpp:video-orientation
a=extmap:5 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01
a=extmap:6 http://www.webrtc.org/experiments/rtp-hdrext/playout-delay
a=extmap:7 http://www.webrtc.org/experiments/rtp-hdrext/video-content-type
a=extmap:8 http://www.webrtc.org/experiments/rtp-hdrext/video-timing
a=extmap:10 http://tools.ietf.org/html/draft-ietf-avtext-framemarking-07
a=recvonly
a=rtcp-mux
a=rtcp-rsize
a=rtpmap:96 VP8/90000
a=rtcp-fb:96 goog-remb
a=rtcp-fb:96 transport-cc
a=rtcp-fb:96 ccm fir
a=rtcp-fb:96 nack
a=rtcp-fb:96 nack pli
a=rtpmap:97 rtx/90000
a=fmtp:97 apt=96
a=rtpmap:98 VP9/90000
a=rtcp-fb:98 goog-remb
a=rtcp-fb:98 transport-cc
a=rtcp-fb:98 ccm fir
a=rtcp-fb:98 nack
a=rtcp-fb:98 nack pli
a=fmtp:98 profile-id=0
a=rtpmap:99 rtx/90000
a=fmtp:99 apt=98
a=rtpmap:100 H264/90000
a=rtcp-fb:100 goog-remb
a=rtcp-fb:100 transport-cc
a=rtcp-fb:100 ccm fir
a=rtcp-fb:100 nack
a=rtcp-fb:100 nack pli
a=fmtp:100 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42001f
a=rtpmap:101 rtx/90000
a=fmtp:101 apt=100
a=rtpmap:102 H264/90000
a=rtcp-fb:102 goog-remb
a=rtcp-fb:102 transport-cc
a=rtcp-fb:102 ccm fir
a=rtcp-fb:102 nack
a=rtcp-fb:102 nack pli
a=fmtp:102 level-asymmetry-allowed=1;packetization-mode=0;profile-level-id=42001f
a=rtpmap:123 rtx/90000
a=fmtp:123 apt=102
a=rtpmap:127 H264/90000
a=rtcp-fb:127 goog-remb
a=rtcp-fb:127 transport-cc
a=rtcp-fb:127 ccm fir
a=rtcp-fb:127 nack
a=rtcp-fb:127 nack pli
a=fmtp:127 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f
a=rtpmap:122 rtx/90000
a=fmtp:122 apt=127
a=rtpmap:125 H264/90000
a=rtcp-fb:125 goog-remb
a=rtcp-fb:125 transport-cc
a=rtcp-fb:125 ccm fir
a=rtcp-fb:125 nack
a=rtcp-fb:125 nack pli
a=fmtp:125 level-asymmetry-allowed=1;packetization-mode=0;profile-level-id=42e01f
a=rtpmap:107 rtx/90000
a=fmtp:107 apt=125
a=rtpmap:108 red/90000
a=rtpmap:109 rtx/90000
a=fmtp:109 apt=108
a=rtpmap:124 ulpfec/90000
```

## 目睹
// answer
```c++
v=0
o=- 4090864225423683934 2 IN IP4 127.0.0.1
s=-
t=0 0
a=group:BUNDLE audio video
a=msid-semantic: WMS
m=audio 9 UDP/TLS/RTP/SAVPF 111 103 104 9 0 8 106 105 13 110 112 113 126
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:O1VN
a=ice-pwd:6TQ2bWmL0yjhTWpN9EHKJGce
a=ice-options:trickle
a=fingerprint:sha-256 3E:7D:57:9C:25:0A:B8:D1:36:3D:51:E8:1C:FC:16:A2:6A:E6:B2:BC:17:90:C5:DA:C2:06:F5:39:2A:B6:E6:27
a=setup:active
a=mid:audio
a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level
a=recvonly
a=rtcp-mux
a=rtpmap:111 opus/48000/2
a=rtcp-fb:111 transport-cc
a=fmtp:111 minptime=10;useinbandfec=1
a=rtpmap:103 ISAC/16000
a=rtpmap:104 ISAC/32000
a=rtpmap:9 G722/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:106 CN/32000
a=rtpmap:105 CN/16000
a=rtpmap:13 CN/8000
a=rtpmap:110 telephone-event/48000
a=rtpmap:112 telephone-event/32000
a=rtpmap:113 telephone-event/16000
a=rtpmap:126 telephone-event/8000
m=video 9 UDP/TLS/RTP/SAVPF 100 101 127 122 96 97 98 99 108 109 124
c=IN IP4 0.0.0.0
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:O1VN
a=ice-pwd:6TQ2bWmL0yjhTWpN9EHKJGce
a=ice-options:trickle
a=fingerprint:sha-256 3E:7D:57:9C:25:0A:B8:D1:36:3D:51:E8:1C:FC:16:A2:6A:E6:B2:BC:17:90:C5:DA:C2:06:F5:39:2A:B6:E6:27
a=setup:active
a=mid:video
a=extmap:2 urn:ietf:params:rtp-hdrext:toffset
a=extmap:3 http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time
a=extmap:4 urn:3gpp:video-orientation
a=extmap:5 http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01
a=extmap:6 http://www.webrtc.org/experiments/rtp-hdrext/playout-delay
a=extmap:7 http://www.webrtc.org/experiments/rtp-hdrext/video-content-type
a=extmap:8 http://www.webrtc.org/experiments/rtp-hdrext/video-timing
a=recvonly
a=rtcp-mux
a=rtcp-rsize
a=rtpmap:100 H264/90000
a=rtcp-fb:100 goog-remb
a=rtcp-fb:100 transport-cc
a=rtcp-fb:100 ccm fir
a=rtcp-fb:100 nack
a=rtcp-fb:100 nack pli
a=fmtp:100 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42001f
a=rtpmap:101 rtx/90000
a=fmtp:101 apt=100
a=rtpmap:127 H264/90000
a=rtcp-fb:127 goog-remb
a=rtcp-fb:127 transport-cc
a=rtcp-fb:127 ccm fir
a=rtcp-fb:127 nack
a=rtcp-fb:127 nack pli
a=fmtp:127 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f
a=rtpmap:122 rtx/90000
a=fmtp:122 apt=127
a=rtpmap:96 VP8/90000
a=rtcp-fb:96 goog-remb
a=rtcp-fb:96 transport-cc
a=rtcp-fb:96 ccm fir
a=rtcp-fb:96 nack
a=rtcp-fb:96 nack pli
a=rtpmap:97 rtx/90000
a=fmtp:97 apt=96
a=rtpmap:98 VP9/90000
a=rtcp-fb:98 goog-remb
a=rtcp-fb:98 transport-cc
a=rtcp-fb:98 ccm fir
a=rtcp-fb:98 nack
a=rtcp-fb:98 nack pli
a=rtpmap:99 rtx/90000
a=fmtp:99 apt=98
a=rtpmap:108 red/90000
a=rtpmap:109 rtx/90000
a=fmtp:109 apt=108
a=rtpmap:124 ulpfec/90000
```
