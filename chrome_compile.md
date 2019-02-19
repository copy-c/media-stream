# window
1.vs2017  
- Windows 10 SDK，通过vs install安装后，需要在应用程序管理中修改Windows Software Development Kit，勾选Debugging Tools For Windows  

2.depot_tools  
- 官网下载后解压，并将目录添加到环境变量Path中  
- 通过执行gclient是否添加成功  

3.download code
- fetch --no-history chromium 

4.compile
- gn args --ide=vs out/xx
```c
    // 加快编译速度与减少包大小
    symbol_level = 0  
    enable_nacl = false
    use_jumbo_build = true
    is_component_build = true
    remove_webcore_debug_symbols = true
    // 功能
    use_openh264 = true
    rtc_use_h264 = true
    rtc_enable_bwe_test_logging = true
    rtc_include_tests=false
    ffmpeg_branding="Chrome"
    proprietary_codecs=true
```
- autoninja -C out/xx chrome

5.run  
chrome.exe --enable-logging --v=1

# linux
1.depot_tools

2.download code
- fetch --no-history chromium 
- ./build/install-build-deps.sh
- gclient runhooks  

3.compile
- gn args out/xx
```c
    // 加快编译速度与减少包大小
    symbol_level = 0  
    enable_nacl = false
    use_jumbo_build = true
    remove_webcore_debug_symbols = true
    // 功能
    use_openh264 = true
    rtc_use_h264 = true
    rtc_enable_bwe_test_logging = true
    rtc_include_tests=false
    ffmpeg_branding="Chrome"
    proprietary_codecs=true
```
- if adjust args, vi args.gn
- autoninja -C out/xx chrome

4.run  
./chrome  
