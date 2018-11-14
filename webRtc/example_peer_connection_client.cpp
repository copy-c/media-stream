https://www.cnblogs.com/CoderTian/p/7868328.html  
分三种类  
MainWnd：实现窗体程序  
PeerConnectionClient：与信令服务器来进行TCP通信  
Conductor：当以上两种类完成某个事件时，会调用相应接口来通知Conductor  



conductor : public MainWndCallback
{
    PeerConnectionClient* client_;
    void StartLogin(const std::string& server, int port) override; // MainWndCallback implementation.
}

MainWnd
{
    MainWndCallback *callback_;
}

// 窗口中处理调用了startlogin
void MainWnd::OnDefaultAction() {
    callback_->StartLogin(server, port);
}
// Conductor又重写了接口，而其中的client_又是PeerConnectionClient类
void Conductor::StartLogin(const std::string& server, int port) {
    server_ = server;
    client_->Connect(server, port, GetPeerName());
}
