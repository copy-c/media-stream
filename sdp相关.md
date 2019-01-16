# 码率相关
## 示例
m=video 9 UDP/TLS/RTP/SAVPF 100  
b=AS:20  
a=fmtp:100 x-google-max-bitrate=30;x-google-min-bitrate=20;x-google-start-bitrate=25
## 规则
1.b 
  >AS 应用的最大带宽  
  >必须要在m=video组内，否则不能生效  
  >设置最大的带宽，且优先级高于x-google-max-bitrate  

2.x-google 
  >a=fmtp:xx 子属性 xx号要绑定相应的编码器  
  >x-google-max-bitrate：视频码流最大值，当网络特别好时，码流最大能达到这个值，如果不设置这个值，网络好时码流会非常大   
  >x-google-min-bitrate：视频码流最小值，当网络不太好时，WebRTC的码流每次5%递减，直到这个最小值为，如果没有设置这个值，网络不好时，视频质量会非常差   
  >x-google-start-bitrate：视频编码初始值，当网络好时，码流会向最大值递增，当网络差时，码流会向最小值递减。

## 源码分析
1.解析保存sdp
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
2.设置码率
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
3.使用码率：网络反馈、编码器使用
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

# rtp/rtcp相关






