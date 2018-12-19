# wireshark命令
udp.stream eq 0
ip.addr eq 101.37.12.221
stun && ip.addr==119.3.63.156

# 服务器信息
192.168.0.101 client
119.3.63.156 server
118.178.135.125 server
101.37.12.221 stun

# 问题现象
10:36:11.061 start 
10:36:11.2114 end
119突然没有响应
119->192 Destination unreachable (Port unreachable)

10:36:44.0882 start 
10:36:44.2147 end
119突然没有给响应
119->192 Destination unreachable (Port unreachable)

10:39:40.4762 start tcp
10:42:35.325 开始返回响应
