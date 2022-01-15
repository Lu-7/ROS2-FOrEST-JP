# FOrESTサンプルプロジェクト-MNIST手書き数字認識のための畳み込みニューラルネットワーク

このサンプルプロジェクトは、MNIST手書き数字認識タスクに適用されているFPGAで実行されている畳み込みニューラルネットワーク（CNN）で構成されています。

## 要件
- FOrESTとそれに関連するすべての要件がZynqボードにインストールおよびセットアップされている。
- VivadoおよびVivado HLS 2019.1。
- Ubuntu18.04を搭載したPC。
- Matplotlib、numpy、tensorflowがインストールされている。： `pip3 install numpy matplotlib tensorflow`
- [ROS2Eloquent](https://docs.ros.org/en/eloquent/Installation.html)がコンピューターにインストールされています。
- PCとZynqボード間でデータを転送するためのネットワーク設定。

## サンプルプロジェクトの実行

### config.forestの設定
config.forestのテンプレート生成

`python3 forest.py -g -i  -o 1`

config.forestの記述
```
**** 1- Setup Information ****

Forest project name:mnist_cnn

Absolute ROS2 dev_ws path:/home/xilinx/dev_ws

Absolute FPGA .bit file path:/home/xilinx/overlays/mnist_cnn.bit

User IP name:cnn_top_0

**** 2- Input definitions ****

// Input 1

Input name:image_in

Protocol:stream

Type:uint8[784]

Address Offset (if AXI-Lite):

**** 3- Output definitions ****

// Output 1

Output name:digit

Protocol:stream

Type:uint8[1]

Address Offset (if AXI-Lite):
```

### PC側での実行
1. VivadoHLSで新しいプロジェクトを作成し、design_files/フォルダからmnist_cnn.cppとすべての.hファイルをインポートする。
また、デザインを合成してIPとしてVivadoにエクスポートします。
2. Vivadoで新しいプロジェクトを作成し、新しいブロックデザインを作成し、手順1でエクスポートしたIPを含めます。
Zynq UltraScale+ MPSoC IPとVivado AXIダイレクトメモリアクセス（DMA）IPも含めます。
IPを統合し、デザインをコンパイルしてビットストリームを生成します。
3. 生成されたビットストリームファイルと.hwhファイル、およびdesign_files/ディレクトリにあるconfig.forestファイルをZynqボードに移動する。
config.forestは、forest.pyファイルと同じフォルダーに配置する必要があります。
4. ros2_packages/内の2つのフォルダをPCのdev_ws/srcの場所に移動し、それらをビルドする。
5. PCでターミナルを2つ起動して、以下の送信ノードと受信ノードを実行する。
```
ros2 run mnist_cnn_send receive

ros2 run mnist_cnn_send send
```

### Zynqボード側での実行
1. FOrESTを実行してROS2-FPGAノードを生成する

`python3 forest.py -t`

2. Zynqボード上で、ROS2-FPGAノードを実行する
```
sudo -s
cd ~/dev_ws/
. install/setup.bash
ros2 run forest_mnist_cnn_fpga_node fpga_node
```
