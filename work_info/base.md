# 部署方法
## 编译mrtc方法
1.编译  
编译环境 docker_build（name） 
docker run -t -i -v /home/yzngo/Documents/:/data registry.cn-hangzhou.aliyuncs.com/myun/build-mrtc
1）创建build目录  
2）  
export CC=clang  
export CXX=clang++  
3）cmake ..  
4）make -j8  
2.打包  
替换docker的二进制文件和lib  
docker build -t registry.cn-hangzhou.aliyuncs.com/myun/name_:tag_ .(dockerfile目录)  
docker build -t registry.cn-hangzhou.aliyuncs.com/myun/mrtc-server:decodec_test .
4.运行镜像
docker run --privileged -idt -e NODE_KEY="" -e HTTPSERVER=http://127.0.0.1/mrtc-gateway/server-callback -e REGISTRY_URL="" -e SERVICE_ADDR="" --name=decodec_test --net=host -v /home/yzngo/Documents/:/data registry.cn-hangzhou.aliyuncs.com/myun/mrtc-server:decodec_test
3.http服务  
python -m SimpleHTTPServer  
4.html demo
http://127.0.0.1:8000/demos/player.html // 拉流端
http://127.0.0.1:8000/demos/publisher.html // 推流端
## 编译webrtc库
gn gen out/x64/Debug '--args=rtc_use_h264=true ffmpeg_branding="Chrome" proprietary_codecs=true target_os="linux" target_cpu="x64"'

./build.sh -b branch-heads/66 -n Debug -d // 第一次拉代码
./build.sh -n Debug -x -d 


# docker命令  
1）获取镜像  
registry.cn-hangzhou.aliyuncs.com/myun/mrtc_server_docker
docker pull registry.cn-hangzhou.aliyuncs.com/myun/build-mrtc  
2）运行镜像    
docker run --privileged -idt -e NODE_KEY="" -e HTTPSERVER=http://127.0.0.1/mrtc-gateway/server-callback -e REGISTRY_URL="" -e SERVICE_ADDR="" --name=mrtc_server_test --net=host -v /home/yzngo/Documents/:/data registry.cn-hangzhou.aliyuncs.com/myun/mrtc-server:rotation // 注意要带上标签  
docker run --privileged -idt -e NODE_KEY="" -e HTTPSERVER=http://127.0.0.1/mrtc-gateway/server-callback -e REGISTRY_URL="" -e SERVICE_ADDR="" --name=mrtc_server_test --net=host -v /home/yzngo/Documents/:/data registry.cn-hangzhou.aliyuncs.com/myun/mrtc_server_docker 
-v /data:/data 是挂载  
/home/yzngo/Documents/:/data  
3）查看正在运行  
docker ps      
4）列出本机上的镜像  
docker image    
5）docker stop  
6）docker exec -it name_ bash   
7）docker push  
8）删除本机镜像  
docker rmi   
9）删除镜像记录

# git命令  
git push origin local:master // local到远端master   
git push origin local:create_branch_name    
git push origin --delete branch_name  // 删除远端分支

git pull origin master:local


# core 文件
core文件放置位置 
echo "/data/core-%e-%t-%p" > /proc/sys/kernel/core_pattern

docker run --privileged -idt -e NODE_KEY="" -e HTTPSERVER=http://127.0.0.1/mrtc-gateway/server-callback -e REGISTRY_URL="" -e SERVICE_ADDR="" --name=decodec_test --net=host -v /home/yzngo/Documents/:/data registry.cn-hangzhou.aliyuncs.com/myun/mrtc-server:decodec_test


# 代理
export https_proxy=http://mudutv:crosswall@mudu.ns.4l.hk:51873
export http_proxy=http://mudutv:crosswall@mudu.ns.4l.hk:51873


# 服务器
47.91.20.112 2iv723ztoi708paw
47.89.193.141 aeha9Phi // 存放webrtc的编译 海外服务器
118.178.135.125 
scp -r root@47.89.193.141:/data/webrtc-builds/out/webrtc-22215-noDe04-linux-x64.zip .
scp -r root@118.178.135.125:/webrtc/webrtc-22215-noDe04-linux-x64.zip .


# Linux命令
1.lsof 
列出当前系统打开的文件
-i 网络连接 :80显示端口 tcp显示

2.find
find ./ -name "*.cc"

3.du  
-h // 按MB显示
-s // 只计算总量


# wireshark抓包
1.抓取rtp包方法  
找到UDP流量，建立对等连接后，浏览器之间会定期发送UDP通信，在基于UDP的RTP通信中，第一个8比特是十六进制数90，通过选择其中之一进行Analyze/Decode As/RTP  
