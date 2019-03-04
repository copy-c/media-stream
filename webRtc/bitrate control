# webrtc 码率控制模块
 - 发送端基于丢包率的码率控制 ——　依靠接收端发送的RTCP RR报文，动态调整发送码率As  
 - 接收端基于延迟的码率控制 —— 依靠包到达的延迟时间，通过到达滤波器，估算网络延迟，再经过过载滤波器判断当前网络拥塞状况，计算出最大码率Ar，得到Ar后，通过remb报文返回发送端  
 - 通过sdp设置码率的上限与下限  
综合As、Ar和配置的上下限，计算出最终码率A  

## Ar计算
### 接收端返回延迟时间
```c++
ReceiveSideCongestionController::OnReceivedPacket()
{
  if (header.extension.hasTransportSequenceNumber)
  {
    remote_estimator_proxy_.IncomingPacket(arrival_time_ms, payload_size, header);
    {
      remote_estimator_proxy.cc
      RemoteEstimatorProxy::IncomingPacket
      {
        // 开始组建TransportFeedBack
        // 组建完成后直接发送给发送端
      }
    }
  }
}
```
### 发送端
```c++
rtcp_receiver.cc
void RTCPReceiver::IncomingPacket(const uint8_t* packet, size_t packet_size)
{
  // 解析包
  ParseCompoundPacket(packet, packet + packet_size, &packet_information)
  {
    case rtcp::TransportFeedback::kFeedbackMessageType: // 使用SEW
      HandleTransportFeedback(rtcp_block, packet_information);
    case rtcp::Remb::kFeedbackMessageType: // 使用Remb
      HandlePsfbApp(rtcp_block, packet_information);
  }

  TriggerCallbacksFromRtcpPacket()
  {
     transport_feedback_observer_->OnTransportFeedback(*packet_information.transport_feedback);
     //RtpTransportControllerSend::OnTransportFeedback
     //GoogCcNetworkController::OnTransportPacketsFeedback
     {
       SendSideBandwidthEstimation::UpdateDelayBasedEstimate(Timestamp at_time, DataRate bitrate) 
      {
        CapBitrateToThresholds() // 更新
      }
     }
  }
}
```

## As 计算
```c++
RTCPReceiver::TriggerCallbacksFromRtcpPacket
{
  (packet_information.packet_type_flags & kRtcpSr)
  {
    rtcp_bandwidth_observer_->OnReceivedRtcpReceiverReport(packet_information.report_blocks, packet_information.rtt_ms, now_ms);
  }
}
RtpTransportControllerSend::OnReceivedRtcpReceiverReport()
RtpTransportControllerSend::OnReceivedRtcpReceiverReportBlocks
{
  GoogCcNetworkController::OnTransportLossReport(TransportLossReport msg) 
  {
    bandwidth_estimation_->UpdatePacketsLost()
    SendSideBandwidthEstimation::UpdatePacketsLost
    {
      SendSideBandwidthEstimation::UpdateEstimate // 更新As
    }
  }
}
```

## 最终用来更新codec和paced
```c++
GoogCcNetworkController::MaybeTriggerOnNetworkChanged
{
  bandwidth_estimation_->CurrentEstimate(&estimated_bitrate_bps, &fraction_loss, &rtt_ms);
}
```

## sdp设置码率上下限
```c++
RtpTransportControllerSend::SetSdpBitrateParameters
{
  controller_->OnTargetRateConstraints(msg)
}
GoogCcNetworkController::OnTargetRateConstraints
{
  GoogCcNetworkController::UpdateBitrateConstraints
}
```

## 核心类 
1.goog_cc_network_control.cc
```c++
void RtpTransportControllerSend::MaybeCreateControllers() { 
  controller_ = controller_factory_fallback_->Create(initial_config_);
  {
    goog_cc_factory.cc
    {
      Create(NetworkControllerConfig config) return absl::make_unique<GoogCcNetworkController>(event_log_, config, true);
    }
  }
  UpdateControllerWithTimeInterval();
  {
    controller_->OnProcessInterval(msg) - GoogCcNetworkController::OnProcessInterval
    {
      update.probe_cluster_configs = UpdateBitrateConstraints(initial_config_->constraints, initial_config_->constraints.starting_rate);
    }
  }
}
```

# 参考
