# MNIST_CNNのFOrEST無し開発

## ROS2-FPGAノード用パッケージの作成
`ros2 pkg create --build-type ament_python mnist_cnn`

## 独自メッセージ用パッケージの作成
`ros2 pkg create --build-type ament_cmake mnist_cnn_interface`

## パッケージのビルド
`colcon build`
