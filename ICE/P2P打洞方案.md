https://www.jianshu.com/p/78ab26a73915  

# P2P（打洞）方案
## 反向链接技术 —— 通信的双方只有一方位于NAT之后
A:位于NAT之后  
B:拥有外网地址  
A可以主动向B进行连接，但B不能主动连接A，B需要给服务器发送请求，让服务器告知A，让A主动再去连接B（反向连接技术）  
## 基于UDP的打洞
### 原理概述  
1.中间服务器作用
1）公网服务器，位于NAT网关后面的client A和B都可以与一台已知的集中服务器建立连接，并通过这台集中服务器了解对方的信息并中转各自的信息  
2）判断client是否位于NAT之后，client与server连接时，server会记录两对地址，一个是client自身IP和端口号，第二个是实际通信的IP和端口号，两个地址作对比后，就可以判断  
2.P2P建立流程  
1）A不知道如何与B发起连接，于是A给集中服务器发送消息，请求集中服务器帮助与客户端B的UDP连接  
2）集中服务器将B的内外网地址发送给A，同时集中服务器将A的内外网地址发给B  
3）当A收到B的地址后，A向B的地址发送UDP包，并且A会自动锁定第一个给出响应的B地址，B也是同理，此时即可连接  
### 典型场景
#### 两客户端位于同一NAT设备后面
按照上面的P2P流程进行建立，中间服务器会分别返回A和B的对方两对地址，建议以内网地址进行建立连接，这样就不用再经过NAT，进而浪费资源  
#### 两客户端位于不同的NAT设备后面
1）A向服务器发送含有A内网地址的登录消息，服务器会记录A的内网地址并记录A连接的外网地址，同理，B也会被记录下来。无论A与B二者中的任何一方向服务器发送P2P请求，服务器都会将其记录下来的两对地址发给A或B。  
#### 两客户端位于两层NAT设备之后
### 问题：UDP在空闲状态下的超时
NAT设备内部有UDP的空闲状态计时器，若一段时间没有UDP数据通信，NAT设备会关掉“洞”，因此双发要发送心跳包以维持“洞”（洞其实是A的NAT中维护的A到B的映射关系，同理，B也一样）    
## 基于TCP的打洞  

# P2P通信标准协议
## STUN
### 简介
#### 作用
基于UDP的穿透NAT方案，它允许应用程序发现它们与公共互联网之间存在的NAT和防火墙及其他类型，也可以让应用程序确定NAT分配给它们的公网IP地址和端口号  
#### 两种请求类型
1.请求/响应类型(request/respond)：由客户端给服务器发送请求，并等待服务器返回响应  
2.指示类型(indication transaction)：由客户端或服务器发送指示，另一方不产生响应  
注意：两种传输类型又能被细分更多的具体类型  
### 报文结构 
#### 头部 —— 20字节
Message Type：
{  
    M11到M0表示方法的12位编码，C1和C0两位表示类的编码，00表示request、01表示indication、10表示success response、11表示error response  
    方法：STUN只定义了一个方法——Binding，可以用于两种请求类型，前者中用来确认NAT给客户端分配的具体绑定，后者可以保持绑定的激活状态  
    类：表示报文类型是请求/成功响应/错误响应/指示  
}  
Message Length：
{  
    存储信息的长度，不包括头部长度    
}  
magic cookie：
{  
    包含固定值0x2112A442，为了前向兼容  
}  
事务ID：
{  
    96位随机数  
    事务：两种类型都包含一个96位的随机数作为事务ID，对于第一种请求/响应类型，事务ID允许作为长连接标识  
}  
#### 属性 —— TLV(Type-Length-Value)
XOR-MAPPED-ADDRESS = Family + X-Prot + X-Address:表示映射过的IP地址和端口  
RESPONSE-ADDRESS:表示响应的目的地址  
ERROR-CODE = error response:响应号  
{  
    400（错误请求）  
    401（未授权）  
}  
### 通信过程
1.配置：客户端配置stun服务器，缺省端口号为3478。使用UDP发送捆绑请求，使用TCP发送共享私密请求  
2.建立连接  
3.客户端发送共享私密请求  
4.服务器收到共享私密请求 -> 验证消息 -> 发送响应 = USERNAME + PASSWORD  
5.客户端发送捆绑请求  
6.服务器收到捆绑请求 -> 验证消息，通过USERNAME和秘钥等 -> 经过一个或者多个NAT，捆绑请求的源IP地址映射为最靠近STUN的NAT分配的IP -> 发送响应，包括最近的NAT的源IP地址和端口号  
7.客户端收到捆绑响应，就可以使用自己的地址与收到的地址做对比  

## TURN
### 简介
TURN协议本身是STUN的一个拓展，绝大部分报文都是STUN类型的，作为STUN的拓展，TURN增加了新的方法(method)和属性(attribute)  
### 交互
#### 分配地址
1.client发送分配请求(Allocate request)到service，携带需要的属性  
{  
    // Allocate属性
    SOFTWARE:提供客户端的软件版本信息  
    LIFTTIME:客户端希望该allocation的生命周期，默认为10分钟  
    REQUESTED-TRANSPORT：服务器与对端之间采用UDP协议  
}  
2.service 收到认证的allocate请求 -> 检查每个属性 -> 产生allocate，发送响应  
{
    分配地址（包括client本地地址/端口、server地址/端口、协议，server保存的是client的nat地址） 
    XOR-RELAYED-ADDRESS属性，值为该allocation的中继传输地址；该响应还包括XOR-MAPPED-ADDRESS属性，值为客户端的server-reflexive地址  
    通过MESSAGE-INTEGRITY属性确保完整性  
}
3.地址分配好后，client必须对其保活，通常的方法是发送刷新请求（Refresh request）到server，中断通信时就发送一个生命期为0的请求  
#### 建立许可
4.客户端准备向peer发送数据，需要创建permission，发送CreatePermission请求，此时携带XOR-PEER-ADDRESS属性包含有peer的IP地址和之前allocate请求中一样的username等  
5.服务器收到CreatePermission请求，产生相应的许可，并且已CreatePremission成功响应来回应  
#### 发送数据 Send（client到server）+ Data（server到peer）
6.客户端使用Send Indication发送数据，peer的传输地址包含在XOR-PEER-ADDRESS属性中，应用数据包含在DATA属性中  
7.服务器收到Send Indication后，提取出应用数据封装成UDP格式，发送给peer  
8.peer回应包含应用数据的UDP包给服务器，当服务器收到后，将生成Data indication消息给客户端  
#### 绑定通道
9.客户端指定一个空闲的通道号包含在CHANNEL-NUMBER属性中，peer的地址包含在XOR-PEER-ADDRESS属性中，发送给服务端  
10.服务端收到请求后，服务器绑定这个peer的通道号，为peer的ip地址安装一个permission，然后给客户端回应ChannelBind成功响应消息  
11.客户端发送ChannelData消息给服务器，不是STUN消息，携带通道号+数据+数据长度，服务器通过通道号发现已经绑定，直接以UDP方式发送给B  
12.peer发送UDP包给服务器，然后回给客户端  
##### Channels与Send/Data的区别
Channel字节比Send/Data少，不使用STUN头部，而使用4字信道号  
Channel有持续时间，默认时间为10分钟，通过重新发送ChannelBind Requset来刷新持续时间

## ICE
### 简介
ICE是一个用于在offer/answer模式下的NAT传输协议，主要用于UDP下多媒体会话的建立  
### 流程
1.依次排序三种可能的传输地址  
直接和网络接口联系的传输地址(host address) HOST CANDIDATE  
经过NAT转换的传输地址，即反射地址(server reflective address) SERVER REFLEXIVE CANDIDATES  
TURN服务器分配的中继地址(relay address) RELAYED CANDIDATES  
2.组成 CANDIDATE PAIRS  
3.连接性检查
终端开始连通性检查，每次检查都是STUN request/response传输 Binding  

## SDP——ICE信息描述符
### 简介
描述格式采用标准的SDP(Session Description Protocol，会话描述协议)  
### SDP格式
会话描述：  
v= (protocol version)  
o= (originator and session identifier)  
s= (session name)  
时间信息描述：  
t= (time the session is active)  
多媒体信息描述：  
m= (media name and transport address)  
// 仍然有许多可选字段 



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
