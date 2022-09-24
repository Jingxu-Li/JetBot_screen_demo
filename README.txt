udp_test 是  jetson Nano 上面代码 使用：
sudo python3 udp_test.py

相机端设备：
执行 server_code 作为主程序
car_state 实现car 类 更新小车状态
image_utils 图像工具 包含图像处理和获取函数
test_udp_server 包含和小车通信的udp函数
trace_target 生成轨迹方法


调试：
所有设备连接热点，处于同一局域网下
各车监听本地23端口，接收指令
指令格式：标识符-数据1-数据2-...-数据n（标识符：l-左转 r-右转 st- 直行 详见代码）




