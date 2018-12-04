# 部署方法
1.编译  
编译环境 docker build（name） 
1）创建build目录  
2）  
export CC=clang  
export CXX=clang++  
3）cmake ..  
4）make -j8  
2.打包  
替换docker的二进制文件和lib  
docker build -t registry.cn-hangzhou.aliyuncs.com/myun/name_:tag_ .(dockerfile目录)  
3.http服务  
python -m SimpleHTTPServer  
4.html demo
http://127.0.0.1:8000/demos/player.html // 拉流端
http://127.0.0.1:8000/demos/publisher.html // 推流端

# docker命令  
1）docker获取镜像  
docker pull registry.cn-hangzhou.aliyuncs.com/myun/build-mrtc  
2）docker运行镜像    
docker run --privileged -idt -e NODE_KEY="" -e HTTPSERVER=http://127.0.0.1/mrtc-gateway/server-callback -e REGISTRY_URL="" -e SERVICE_ADDR="" --name=mrtc_server_test --net=host -v /home/yzngo/Documents/:/data registry.cn-hangzhou.aliyuncs.com/myun/mrtc-server:rotation // 注意要带上标签  
-v /data:/data 是挂载  
/home/yzngo/Documents/:/data  
3）docker ps     
查看正在运行的容器  
4）docker image  
列出本机上的镜像  
5）docker stop  
6）docker exec -it name_ bash   
7）docker push  

# git命令  
git push origin test:master // 本地test到远端master  
