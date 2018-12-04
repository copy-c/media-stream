https://blog.csdn.net/NB_vol_1/article/details/82119450  
https://www.jianshu.com/u/01c225e97375   
https://blog.csdn.net/liuhongxiangm/article/details/53581064  
# 视频采集
## 基本数据结构 
```c++
class VideoFrameBuffer <<interface>>
[
    class VideoFrame;
    class I420
]
```
## pc
```c++
// 发送端
peerconnection_client
{
    // conductor.cc
    1.InitializePeerConnection
    {
        1.1 peer_connection_factory_ = CreatePeerConnectionFactory(); 
        1.2 CreatePeerConnection()
        {
            peer_connection_ = peer_connection_factory_->CreatePeerConnection();
        }
        1.3 AddTrack() // 发送端才进行这一步，比如publisher并没有这步而player才有
        {
            // peerconnection.cc
            1.3.1 scoped_refptr<webrtc::VideoTrackInterface> video_track_ = peer_connection_factory_->CreateVideoTrack(CreateVideoSource);
            {
                rtc::scoped_refptr<VideoTrackInterface> track(VideoTrack::Create(id, source, worker_thread_));
                return VideoTrackProxy::Create(signaling_thread_, worker_thread_, track);
            }
            1.3.2 peer_connection_->AddTrack(video_track_, {kStreamId});
            {
                // 此时video_track_变为基类MediaStreamTrackInterface
                // VideoTrackInterface::public MediaStreamTrackInterface
                1.3.2.1 AddTrackUnifiedPlan
                {
                    // 此时track和sender绑定到一起了
                    1.3.2.1.1 auto sender = CreateSender(media_type, sender_id, track, stream_ids);
                    1.3.2.1.2 auto receiver = CreateReceiver(media_type, rtc::CreateRandomUuid());
                    1.3.2.1.3 transceiver = CreateAndAddTransceiver(sender, receiver);
                    {
                        RtpTransceiver transceiver;
                        transceiver_.push_back(transceiver); // vector<rtc::scoped_refptr<RtpTransceiverProxyWithInternal<RtpTransceiver>> transceiver_
                    }
                }
            }
        }
    }
    2 CreateOffer
    peer_connection_->CreateOffer(this, webrtc::PeerConnectionInterface::RTCOfferAnswerOptions());
    {
        // peerconnection.cc
        // observer 是conductor的this
        webrtc_session_desc_factory_->CreateOffer(observer, options, session_options); //unique_ptr<WebRtcSessionDescriptionFactory> webrtc_session_desc_factory_;
    }
    3 Conductor::OnSuccess // offer发送成功后回调
    {
        peerconnection.cc
        // 3.1 保存localDsp
        SetLocalDescription
        {
            ApplyLocalDescription(std::move(desc))
            {
                PushdownTransportDescription()
                {
                    transport_controller_->SetLocalDescription(type, sdesc->description()); //unique_ptr<JsepTransportController> transport_controller_;
                }
                UpdateTransceiversAndDataChannels()
                {
                    AssociateTransceiver()
                    {
                        // 没看太懂，应该是sdp中的name绑定创建pc那里创建的transceiver
                    }
                    UpdateTransceiverChannel()
                    {
                        // 增加channel给transceiver
                        channel = CreateVideoChannel(content.name);
                        transceiver->internal()->SetChannel(channel);
                        // 调用方法
                        cricket::BaseChannel* channel = transceiver->internal()->channel();
                    }
                    transceiver->internal()->sender_internal()->set_stream_ids(streams[0].stream_ids()); // 绑定stream
                    transceiver->internal()->sender_internal()->SetSsrc(streams[0].first_ssrc());
                }
            }
        }
        // 3.2 创建answer
        CreateSessionDescription()
        // 3.3 保存remoteDsp
        peer_connection_->SetRemoteDescription()
        {
            // 绑定transceiver和创建channel与local相同
            // 增加streams到reveiver 
            transceiver->internal()->receiver_internal()->SetStreams(media_streams); // scoped_refptr<RtpReceiverInternal> receiver_internal()
            // 回调
            for (auto transceiver : now_receiving_transceivers) {
                stats_->AddTrack(transceiver->receiver()->track());
                observer->OnTrack(transceiver);
                observer->OnAddTrack(transceiver->receiver(), transceiver->receiver()->streams());
            }
            for (auto stream : added_streams) {
                observer->OnAddStream(stream);
            }
        }
    }
    
}


// 接受端
// 收到offer后
// 保存远端 SetRemoteDescription
// 创建answer并发送成功后，回调
// 保存本地 SetLocalDescription
```




# 媒体相关类
## pc 目录下
最顶层为MediaStream，pc创建中会把下面的创建好

class MediaStreamInterface : public rtc::RefCountInterface,
                             public NotifierInterface {}
class MediaStream : public Notifier<MediaStreamInterface>

class MediaStreamTrackInterface {}
class VideoSourceInterface {AddOrUpdateSink();}
class VideoTrackInterface : public MediaStreamTrackInterface,
                            public rtc::VideoSourceInterface<VideoFrame> {}

peerconnection.cc
{
    
    // sender端 先手offer
    InitializePeerConnection()
    {
        CreatePeerConnection();
        AddTracks()
        {
            VideoTrackInterface video_track_ = CreateVideoTrack(CreateVideoSource); // 将源的track取出来
            peer_connection_->AddTrack(video_track_, {kStreamId}) // video_track_ 是 MediaStreamTrackInterface
            {
                sender = new RtpSenderInternal;
                receiver = new RtpReceiverInternal;
                transceiver = <RtpTransceiver>::Create(new RtpTransceiver(sender, receiver));
                transceivers_.push_back(transceiver);
            }
        }
    }
    
    ApplyLocalDescription(
    {
        // 创建channel
        // video->name 是从dsp中获取的，其实是一个标识，mid
        cricket::VideoChannel* video_channel = CreateVideoChannel(video->name);
        {
            cricket::VideoChannel* video_channel = channel_manager()->CreateVideoChannel
            {
                call_.get() // 此处的call_是pc的成员变量
                通过channelmanager.cc来进行管理，都是由它进行创建
            }

        }
        
    }

    // receiver端 收到offer
    rtc::scoped_refptr<StreamCollection> remote_streams_;
    ApplyRemoteDescription()
    {
        // 根据收到的stream_id创建stream并加入
        remote_streams_->(stream);
        media_streams.push_back(stream);
        // 加入transceiver中
        transceiver->internal()->receiver_internal()->SetStreams(media_streams);
        now_receiving_transceivers.push_back(transceiver);
        // 加入回调 PeerConnectionObserver
        // 但感觉这边已经是被解码的内容啊，所以 video的那些和pc的这些的关系是什么，主要这个问题
        observer->OnTrack(transceiver);
        observer->OnAddTrack(transceiver->receiver(), transceiver->receiver()->streams());
        observer->OnAddStream(stream);
    }
}

// 先分析receiver
rtpreceiver.cc
RtpReceiverInternal : public RtpReceiverInterface
VideoRtpReceiver : public rtc::RefCountedObject<RtpReceiverInternal>
{
    class VideoRtpTrackSource : public VideoTrackSource 
    {
        rtc::VideoBroadcaster broadcaster_;
    }
    source_(new RefCountedObject<VideoRtpTrackSource>());
    cricket::VideoMediaChannel* media_channel_ = nullptr;

}

VideoTrackSource : public Notifier<VideoTrackSourceInterface>
VideoTrackSourceInterface : public MediaSourceInterface,
                            public rtc::VideoSourceInterface<VideoFrame>


VideoSourceBase : public VideoSourceInterface<webrtc::VideoFrame>



## 找video的指针 都是video目录
方法：
取VideoReceiveStream
webrtcvideoengine.cc
// 
class WebRtcVideoChannel : public VideoMediaChannel
{
    std::map<uint32_t, WebRtcVideoReceiveStream*> receive_streams_ RTC_GUARDED_BY(stream_crit_);
    
    class WebRtcVideoReceiveStream: public rtc::VideoSinkInterface<webrtc::VideoFrame> 
    {
        webrtc::Call* call;
        webrtc::VideoReceiveStream* stream_;
    }
    
    AddRecvStream(const StreamParams& sp)
    {
        receive_streams_[ssrc] = new WebRtcVideoReceiveStream();
    }
}

video_receive_stream.cc
VideoReceiveStream
{
    rtp_video_stream_receiver_(&transport_adapter_,
                                 call_stats,
                                 packet_router,
                                 &config_,
                                 rtp_receive_statistics_.get(),
                                 &stats_proxy_,
                                 process_thread_,
                                 this,   // NackSender
                                 this,   // KeyFrameRequestSender
                                 this),  // OnCompleteFrameCallback

    RequestKeyFrame();
    {
        return rtp_video_stream_receiver_.RequestKeyFrame()
    }

    RtpVideoStreamReceiver rtp_video_stream_receiver_;
}

rtp_video_stream_receiver.h
RtpVideoStreamReceiver
{
    const std::unique_ptr<RtpRtcp> rtp_rtcp_;
    int32_t RequestKeyFrame() override;
    {
        return rtp_rtcp_->RequestKeyFrame();
    }
}

rtp_rtcp_impl.cc
class ModuleRtpRtcpImpl : public RtpRtcp
{
    SetKeyFrameRequestMethod(const KeyFrameRequestMethod method)
    {
        key_frame_req_method_ = method;
    }

    int32_t RequestKeyFrame()
    {
        switch (key_frame_req_method_) {
            case kKeyFrameReqPliRtcp:
                return SendRTCP(kRtcpPli);
            case kKeyFrameReqFirRtcp:
                return SendRTCP(kRtcpFir);
        }
    }
}

# channel
class MediaChannel {}
class VideoMediaChannel : public MediaChannel {}
class WebRtcVideoChannel : public VideoMediaChannel
{
    std::map<uint32_t, WebRtcVideoReceiveStream*> receive_streams_ RTC_GUARDED_BY(stream_crit_);
    
    class WebRtcVideoReceiveStream: public rtc::VideoSinkInterface<webrtc::VideoFrame> 
    {
        webrtc::Call* call;
        webrtc::VideoReceiveStream* stream_;
    }
}

class VideoChannel : public BaseChannel
{
    VideoChannel* ChannelManager::CreateVideoChannel
    {
        VideoMediaChannel* media_channel = media_engine_->CreateVideoChannel(call, media_config, options);

        video_channel = absl::make_unique<VideoChannel>(
            worker_thread_, network_thread_, signaling_thread,
            absl::WrapUnique(media_channel), content_name, srtp_required,
            crypto_options);
    }

    VideoMediaChannel* media_channel() const override {
        return static_cast<VideoMediaChannel*>(BaseChannel::media_channel());
    }
}


WebRtcVideoChannel* WebRtcVideoEngine::CreateChannel()
channelmanager.cc - pc
class MediaEngineInterface
{
    virtual VoiceMediaChannel* CreateChannel
    virtual VideoMediaChannel* CreateVideoChannel
}

### 当前audio的方案
std::vector<AudioSendStream*> GetSendingStreams();              {

}            

auto it = sendingStreams_.begin();
while (++it != sendingStreams_.end()) {
    const webrtc::voe::ChannelProxy &channel = static_cast<webrtc::internal::AudioSendStream *>(*it)->GetChannelProxy();
    channel.GetRtpRtcp(&RtpRtcp, &RtpReceiver);
    rtpRtcps_.push_back(RtpRtcp);
}

# 方案
```c++
peerconnectionfactory.cc
{
    cricket::ChannelManager* PeerConnectionFactory::channel_manager() 
    {
        return channel_manager_.get();
    }
}

channelmanager.cc
ChannelManager
{
    std::vector<std::unique_ptr<VideoChannel>> video_channels_;
}

channel.cc
VideoChannel
{
    VideoMediaChannel* media_channel() const override 
    {
        return static_cast<VideoMediaChannel*>(BaseChannel::media_channel());
    }
}

// 所以这里的media_channel()是不是可以指WebRtcVideoChannel
webrtcvideoengine.cc
WebRtcVideoChannel:public VideoMediaChannel, public webrtc::Transport
{
    std::map<uint32_t, WebRtcVideoReceiveStream*> receive_streams_ RTC_GUARDED_BY(stream_crit_);
}
WebRtcVideoReceiveStream
{
    webrtc::VideoReceiveStream* stream_;
}

video_receive_stream.cc
VideoReceiveStream
{
    void RequestKeyFrame() override;
}
```
## video
### 接收
WebRtcVideoChannel::OnPacketReceived(rtc::CopyOnWriteBuffer* packet,
                                     const rtc::PacketTime& packet_time) 
{
    call_->Receiver()->DeliverPacket(webrtc::MediaType::VIDEO, *packet, packet_time);
}

call.cc
PacketReceiver::DeliveryStatus Call::DeliverPacket()
{
    return DeliverRtcp(media_type, packet.cdata(), packet.size())
    ||
    return DeliverRtp(media_type, std::move(packet), packet_time_us);
    {
        RtpStreamReceiverController video_receiver_controller_;
        video_receiver_controller_.OnRtpPacket(parsed_packet)
        {
            return demuxer_.OnRtpPacket(packet); // RtpDemuxer demuxer_
            {
                RtpVideoStreamReceiver::OnRtpPacket()
                {
                      ReceivePacket(packet);
                }
            }
        }
    }
}

### 解码
video_receive_stream.cc
VideoReceiveStream
{
    // 解码线程启动
    Start() // 继承自call的 webrtc::VideoReceiveStream
    {
        video_receiver_.DecoderThreadStarting(); // vcm::VideoReceiver video_receiver_;
        decode_thread_.Start(); // rtc::PlatformThread decode_thread_;
        rtp_video_stream_receiver_.StartReceive(); 
        {
            // RtpVideoStreamReceiver rtp_video_stream_receiver_;
            void RtpVideoStreamReceiver::StartReceive() {
                receiving_ = true;
            }
        }
    }
    // 编完完成后一顿回调
    IncomingVideoStream::OnFrame[将帧放入队列VideoRenderFrames]
}
