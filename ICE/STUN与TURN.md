https://www.jianshu.com/p/78ab26a73915  

# 基本

# 当前
```c++
bool Publisher::CreatePeerConnection(bool dtls)
{
    // ICE框架下
    // STUN
    webrtc::PeerConnectionInterface::IceServer stun_server;
    stun_server.uri = kIceServerUri; // kStunServerUri = "stun:xx.xx.xx.xx:xx"
    configuration.servers.push_back(stun_server);
    // TURN
    webrtc::PeerConnectionInterface::IceServer turn_server;
    turn_server.uri = kTurnServerUri; // kTurnServerUri = "turn:xx.xx.xx.xx:xx"
    turn_server.password = kTurnServerPassword; 
    turn_server.username = kTurnServerUsername;
    configuration.servers.push_back(turn_server);

    PeerConn_ = PeerConnFactory_->CreatePeerConnection(configuration, nullptr, nullptr, &PCObs_);
    {
        pc->Initialize(configuration, move(allocator),move(cert_generator), observer))
        {
            network_thread() -> bind(InitializePortAllocator_n, configuration)
            {
                port_allocator_->Initialize(); //unique_ptr<PortAllocator> port_allocator_
                port_allocator_->SetConfiguration(stun_servers, turn_servers, configuration);
            }
            transport_controller_.reset(CreateTransportController(port_allocator_.get(), configuration));
        }
    }
}
```
