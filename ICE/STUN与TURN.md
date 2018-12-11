https://www.jianshu.com/p/78ab26a73915  

# P2P通信标准协议
## STUN
### 简介
#### 两种请求类型
1.请求/响应类型(request/respond)：由客户端给服务器发送请求，并等待服务器返回响应  
2.指示类型(indication transaction)：由客户端或服务器发送指示，另一方不产生响应  
注意：两种传输类型又能被细分更多的具体类型  
#### 基本结构
1.报文信息中都含有一个固定头部，包含了方法、类和事务ID  
方法：STUN只定义了一个方法——Binding，可以用于两种类型，前者可以用来确认NAT给客户端分配的具体绑定，后者可以保持绑定的激活状态  
类：表示报文类型是请求/成功响应/错误响应/指示
事务：两种类型都包含一个96位的随机数作为事务ID，对于第一种请求/响应类型，事务ID允许作为长连接标识  
2.内容  
属性：使用TLV编码，交换主要信息  
### 报文结构 
#### 头部 —— 20字节
Message Type：M11到M0表示方法的12位编码，C1和C0两位表示类的编码，00表示request、01表示indication、10表示success response、11表示error response  
Message Length：存储信息的长度，不包括头部长度    
magic cookie：包含固定值0x2112A442，为了前向兼容  
事务ID：96位随机数  
#### 属性
属性TLV(Type-Length-Value)编码，Type和Length都是16位，Value是32位  
典型属性：  
XOR-MAPPED-ADDRESS = Family + X-Prot + X-Address  
ERROR-CODE = error response  
### 通信过程
#### 1.产生一个request或indication  
#### 2.发送request或indication  
2.1 通过UDP发送  
通过客户端业务层重发request保证可靠性  
2.2 通过TCP发送  
#### 3.接收消息
3.1 处理Request  
检查完后，根据检查结果发送响应：Success Response或Error Response
3.2 处理Indication  
若包含未知的强制理解属性，则报文会被忽略并丢弃，若正常则服务端进行相应的处理  
3.3 处理Success Response  
若包含未知的强制理解属性，则被忽略并认为此次传输失败  
3.4 处理Error Response  
根据错误码产生不同的处理方法，包括重新传输  

## TURN
### 简介
TURN协议本身是STUN的一个拓展，绝大部分报文都是STUN类型的，作为STUN的拓展，TURN增加了新的方法(method)和属性(attribute)  
### 传输
1.server(TURN)与peer之间的连接都是基于UDP的，但是服务器和客户端之间可以通过各种连接来传输STUN报文。  
2.client若使用了TCP，也会在服务端转换为UDP，因此建议client使用UDP传输。  
3.支持TCP的原因：一部分防火墙会完全阻挡UDP数据，而对三次握手的TCP数据则不做隔离。  
### 分配(Allocations)
1.client发送分配请求(Allocate request)到server ->server返回分配成功响应，包含分配地址（client可以在属性字段描述其想要的分配类型）  
2.中继地址分配好后，client必须对其保活，通常的方法是发送刷新请求（Refresh request）到server，中断通信时就发送一个生命期为0的请求  
3.server和client都保存一个五元组（包括client本地地址/端口、server地址/端口、协议，server保存的是client的nat地址）  
### 发送机制 —— 关键在于server要管理好peer和client的配对
peer与client之间有两种方法交换信息，两种方法都为了使不同peer和client正确配对  
#### Send Mechanism
Send（client到server）+ Data（server到peer）
Send/Data不支持验证，因此client在给对等端发送indication之前，先安装一个到对等端的许可，否则会被丢弃  
#### Channels
字节比Send/Data少，不使用STUN头部，而使用一个4字节头部，包含了叫做信道号的值，每个信道号都与一个特定的peer绑定，作为对等端地址的一个记号  
channel也有持续时间，默认时间为10分钟，并且可以通过重新发送ChannelBind Requset来刷新持续时间

## ICE
### SDP——ICE信息描述符
#### 简介
ICE信息的描述格式采用标准的SDP(Session Description Protocol，会话描述协议)  
#### SDP信息
#### SDP格式
会话描述：  
v= (protocol version)  
o= (originator and session identifier)  
s= (session name)  
时间信息描述：  
t= (time the session is active)  
多媒体信息描述：  
m= (media name and transport address)  
// 仍然有许多可选字段  
### ICE
#### 简介
ICE是一个用于在offer/answer模式下的NAT传输协议，主要用于UDP下多媒体会话的建立  
#### 流程
1.依次排序三种可能的传输地址  
直接和网络接口联系的传输地址(host address) HOST CANDIDATE  
经过NAT转换的传输地址，即反射地址(server reflective address) SERVER REFLEXIVE CANDIDATES  
TURN服务器分配的中继地址(relay address) RELAYED CANDIDATES  
2.进行配对，组成 CANDIDATE PAIRS  
3.连接性检查
终端开始连通性检查，每次检查都是STUN request/response传输 Binding  
1)为中继候选地址生成许可(Permissions)  
2)从本地候选往远端候选发送Binding Request  
> 此时的Binding带有特殊属性
- PRIORITY: 指明优先级  
- ICE-CONTROLLED和ICE-CONTROLLING: 指明终端是受控方还是主控方  
- Credential: 身份 
3)处理Response  
- 失败响应：  
- 成功响应：response的IP+端口 = Binding Requset的IP+端口  




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
