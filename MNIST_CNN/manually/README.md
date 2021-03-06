# MNIST_CNNのFOrEST無し開発


## 独自メッセージ用パッケージの作成
`cd ~/dev_ws/src`

`ros2 pkg create --build-type ament_cmake mnist_cnn_interface`

- メッセージ用ディレクトリの作成

```
cd mnist_cnn_interface
mkdir msg
```

- メッセージファイルを作成する

```
cd msg
touch FpgaIn.msg FpgaOut.msg
```

- メッセージファイルを編集する

FpgaIn.msg
```
uint8[784] image_in
```

FpgaOut.msg
```
uint8[1] digit
```

- CMakeLists.txtの２３行目に以下のコードを追加する
```
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
        "msg/FpgaIn.msg"
        "msg/FpgaOut.msg"
)
```

- package.xmlの１５行目に以下のコードを追加する
```
  <build_depend>rosidl_default_generators</build_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>
  <member_of_group>rosidl_interface_packages</member_of_group>
```


## ROS2-FPGAノード用パッケージの作成

`cd ~/dev_ws/src`

`ros2 pkg create --build-type ament_python mnist_cnn`

- package.xmlの１５行目に以下のコードを追加
```
  <exec_depend>rclpy</exec_depend>
  <exec_depend>mnist_cnn_interface</exec_depend>
```

- setup.pyの２２行目に以下のコードを追加
```
    entry_points={
        'console_scripts': [
                'fpga_node = mnist_cnn.fpga_node:main',
        ],
    },
```

## ros2-fpgaノードの作成

1. mnist_cnn/mnist_cnn/にfpga_node.pyを作成する

 `cd ~/dev_ws/src/mnist_cnn/mnist_cnn/`
 
`touch fpga_node.py`

2. 手順書のmnist_cnn/fpga_node.pyを見て，fpga_node.pyを編集する

`vim fpga_node.py`



## パッケージのビルド
```
cd ~/dev_ws/
colcon build
````

## 動作確認

### Zynqボード側での実行
```
sudo -sE
cd ~/dev_ws/
. install/setup.bash
ros2 run mnist_cnn fpga_node
```


### PC側での実行
ターミナル1
```
cd ~/dev_ws/
. install/setup.bash
ros2 run mnist_cnn_send receive
```

ターミナル2
```
cd ~/dev_ws/
. install/setup.bash
ros2 run mnist_cnn_send send
```
