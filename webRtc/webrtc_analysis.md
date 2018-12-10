# 参考
1.https://blog.csdn.net/liuhongxiangm/article/details/53581064  
2.https://www.cnblogs.com/fangkm/p/4370492.html  
3.https://blog.piasy.com/2018/05/24/WebRTC-Video-Native-Journey/  
# pc 初始化
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
            {
                PeerConnectionFactory::CreatePeerConnection() / peerconnectionfactory.cc
                {
                      std::unique_ptr<Call> call = worker_thread_->Invoke<std::unique_ptr<Call>>(Bind(&PeerConnectionFactory::CreateCall_w);
                      scoped_refptr<PeerConnection> pc(new rtc::RefCountedObject<PeerConnection>(this, std::move(event_log), std::move(call)));
                }
            }
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
                    transport_controller_->SetLocalDescription(type, sdesc->description()); 
                    //unique_ptr<JsepTransportController> transport_controller_;
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
                        ///// 挺重点的
                        cricket::VideoChannel* channel = CreateVideoChannel(content.name);
                        {
                            // Call 第一次出现在这里，call_.get() ------ 这个call_是如何赋值的
                            cricket::VideoChannel* video_channel = 
                            channel_manager()->CreateVideoChannel(call_.get(), configuration_.media_config, rtp_transport,
                                                                  signaling_thread(), mid, SrtpRequired(),
                                                                  factory_->options().crypto_options, video_options_);
                            // channel_manager() 连接的定义
                            cricket::ChannelManager* PeerConnection::channel_manager() const 
                            {
                                return factory_->channel_manager();
                            }
                            // 进入ChannelManager看它定义的CreateVideoChannel
                            channelmanager.cc
                            {
                                // 第一步：获取构造函数需要的VideoMediaChannel指针
                                // 疑问：media_engine_ 这个函数的指针是如何而来的
                                VideoMediaChannel* media_channel = 
                                media_engine_->CreateVideoChannel(call, media_config, options);
                                {
                                    // 关于media_engine_的定义 MediaEngineInterface，来自mediaengin.cc
                                    // class CompositeMediaEngine : public MediaEngineInterface 来自mediaengin.cc
                                        {
                                            virtual VideoMediaChannel* CreateVideoChannel(call, config, options) {
                                                return video().CreateChannel(call, config, options);
                                            }
                                        }
                                    // 使用CompositeMediaEngine在webrtcmediaengine.cc
                                        {
                                            webrtcmediaengine.cc new了CompositeMediaEngine的对象
                                            其中video使用了WebRtcVideoEngine类 webrtcvideoengine.cc
                                            WebRtcVideoChannel* WebRtcVideoEngine::CreateChannel() {
                                                return new WebRtcVideoChannel(call, config, options);
                                            }
                                        }
                                }
                                // 第二步：
                                video_channel = absl::make_unique<VideoChannel>(
                                                            worker_thread_, network_thread_, signaling_thread,
                                                            absl::WrapUnique(media_channel), content_name, srtp_required,
                                                            crypto_options);
                                video_channels_.push_back(std::move(video_channel));
                        }
                        transceiver->internal()->SetChannel(channel);
                        // 调用方法
                        cricket::BaseChannel* channel = transceiver->internal()->channel();
                    }
                    transceiver->internal()->sender_internal()->set_stream_ids(streams[0].stream_ids()); // 绑定stream
                    transceiver->internal()->sender_internal()->SetSsrc(streams[0].first_ssrc());
                }
            }
            UpdateSessionState(type, cricket::CS_LOCAL, remote_description()->description())
            {
                PushdownMediaDescription(type, source)
                {
                    channel->SetLocalContent(content_desc, type, &error) // 加入send stream
                    channel->SetRemoteContent(content_desc, type, &error) // 加入receive stream
                    {
                        UpdateRemoteStreams_w(video->streams(), type, error_desc);
                        {
                            bool BaseChannel::AddRecvStream_w(const StreamParams& sp) 
                            {
                                return media_channel()->AddRecvStream(sp); // media_channel会指向webrtcvideochannel
                                {
                                    // webrtcvideochannel
                                    receive_streams_[ssrc] = new WebRtcVideoReceiveStream(call_, sp, std::move(config), decoder_factory_, 
                                                                                          default_stream, recv_codecs_, flexfec_config);
                                    // 此处还差一个WebRtcVideoReceiveStream里面VideoReceiveStream的指针
                                    {
                                        WebRtcVideoReceiveStream的构造函数
                                        {
                                            RecreateWebRtcVideoStream()
                                            {
                                                // 此时的stream_是webrtc::VideoReceiveStream
                                                stream_ = call_->CreateVideoReceiveStream(std::move(config));
                                                {
                                                    // call.h
                                                    // 此时的receive_stream是internal::VideoReceiveStream 
                                                    // 他们的关系是internal::VideoReceiveStream : public webrtc::VideoReceiveStream
                                                    VideoReceiveStream* receive_stream = new VideoReceiveStream();  
                                                    {
                                                        rtp_video_stream_receiver_(&transport_adapter_,
                                                                                   call_stats,   
                                                                                   packet_router) // 此处的网络router是如何来的，call是谁传进去的
                                                                                                  // call 是哪里来的啊
                                                    }  
                                                }
                                                stream_->Start();  // 就在此处开始解码
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
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

# 媒体相关
## 基本数据结构 
```c++
class VideoFrameBuffer <<interface>>
{
    class VideoFrame;
    class I420
}
```
## 发送与接收模块关系
https://blog.csdn.net/NB_vol_1/article/details/82118830  

## 核心模块
VideoSendStream
{
    1.提供数据源 capture
    2.提供数据输出点 transport
    3.视频编码器 encode
    4.数据打包 rtp
    5.抗丢包 udp
    6.拥塞控制
    VideoStreamEncoder 处理编码过程
    VideoSendStreamImpl 处理发送过程
}

## 数据源与数据输出点
```c++
template <typename VideoFrameT>
class VideoSourceInterface {
public:
    virtual void AddOrUpdateSink(VideoSinkInterface<VideoFrameT>* sink, const VideoSinkWants& wants) = 0;
    virtual void RemoveSink(VideoSinkInterface<VideoFrameT>* sink) = 0;
protected:
    virtual ~VideoSourceInterface() {}
};
//数据源模可以产生数据，一般来说Capture就是一个数据源；
//产生数据之后，可以通过数据输出点把数据传输到下一个模块，一般来说是编码器模块。


VideoSinkInterface
template <typename VideoFrameT>
class VideoSinkInterface {
public:
    virtual ~VideoSinkInterface() = default;
    virtual void OnFrame(const VideoFrameT& frame) = 0;
    virtual void OnDiscardedFrame() {}
};
//模块之间的数据传输通道，利于模块间解耦
//VideoSinkInterface 主要用于Capture与编码器、解码器与render之间的数据传输。
```

## channel
```c++
pc时候创建channel就已经创建好 WebRtcVideoChannel
问题2.call在具体实现中的作用
webrtcvideoenine.h
WebRtcVideoChannel
{
    AddRecvStream(sp)
    {
        receive_streams_[ssrc] = new WebRtcVideoReceiveStream(call_, sp, std::move(config), decoder_factory_, 
                                                              default_stream, recv_codecs_, flexfec_config);
        // 问题
        // 1.此处WebRtcVideoReceiveStream的内部成员VideoReceiveStream是怎么搞进去的
        {
            
        }
    }
}
```


## 接收
```c++
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
```

## 解码
```c++
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
```

# 需求
## 请求关键帧
当前修改位置
1.peerconnectioninterface.h 增加virtual接口
2.peerconnection.h 通过channle_manager()获取channel信息 RequestKeyFrame
3.channelmanger.h 遍历所有的Videochannel RequestKeyFrameOnVideoChannel
4.webrtcvideoengin.h 遍历所有WebRtcVideoReceiveStream，请求其中VideoReceiveStream的RequestKeyFrameOnMediaChannel
```c++
VideoReceiveStream
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
```



# 其他
## channel
```C++
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
```
