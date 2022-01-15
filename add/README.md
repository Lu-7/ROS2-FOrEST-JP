# FOrEST入門チュートリアル（加算器の例） 
このチュートリアルでは、ROS2-FOrESTを使用してFPGAロジックをROS2システムに組み込む例を示します。
#### このチュートリアルでは以下について学ぶことができます。
1. 設定ファイルのテンプレート（config.forest）を生成する方法と、FPGAデザインから適切な情報を入力する方法
2. ROS2-Forestツールを実行し、FPGAロジックと通信するためのPYNQドライバーを含むROS2パッケージを生成する方法
3. ROS2-FPGAノードの動作を確認するための、単純なTalkerノードとListenerノードを生成する方法
4. FOrESTを使用する際の制限と設計上の考慮事項

# はじめに
このチュートリアルでは、以下に示す単純なHLSデザインであるaddモジュールを使用します。FOrESTを使用して、addモジュールをROS2システムに組み込みます。
```
void add(int a, int b, int c[1]) {

#pragma HLS INTERFACE s_axilite port=a
#pragma HLS INTERFACE s_axilite port=b
#pragma HLS INTERFACE s_axilite port=c
#pragma HLS INTERFACE s_axilite port=return

  c[0]= a+b;

}
```
このデザインは、2つの整数変数を加算する加算器モジュールで構成されています。演算結果はint配列cに配置されます。

このデザインをFOrESTで使用するための最初のステップは、従来のVivadoHLSデザインプロセスに従うことです。
1. Vivado HLSを用いて、HLSデザインを合成しIPをエクスポートする
2. 生成したIPをVivadoでインポートする
3. Vivadoを用いて、他のPYNQオーバーレイと同様に、ZynqのPS部分と統合する
4. ビットストリームを生成する
PYNQオーバーレイの作成に慣れていない場合は、PYNQドキュメントを参照してください。

HLSIPをZynqPSと統合し、ビットストリームを生成すると、PYNQドライバが必要とする.bitファイルと.hwhファイルが作成されます。これらのファイルを、FOrESTを実行するPYNQシステムにコピーする必要があります。

# 設定ファイル-config.forest
次のステップは、システムに関する情報を含む設定ファイルであるconfig.forestの生成と設定です。FOrESTはconfig.forestに記述された情報を基にROS2-FPGAノード及びROS2パッケージなどの関連ファイルを生成します。

config.forestをforest.pyスクリプトが配置されているディレクトリに移動して実行することにより、テンプレートであるconfig.forestファイルを生成できます。

`python3 forest.py -g -i 2 -o 1`
-gフラグは、config.forestを生成するためのオプションです。-iとは-o、それぞれ、FPGAロジックが持つ入力信号と出力信号を入力してください。加算器モジュールには、2つの入力（int aおよびint b）と1つの出力（int c[1]）があります。

このコマンドを実行すると、forest.pyスクリプトと同じディレクトリにconfig.forestファイルが作成されます。

次に、config.forestファイルにFPGAロジックに関する情報を入力する必要があります。このチュートリアルで使用するconfig.forestファイルを以下に示します。

```
**** 1- Setup Information ****

Forest project name:simple_add

Absolute ROS2 dev_ws path:/home/xilinx/dev_ws

Absolute FPGA .bit file path:/home/xilinx/PYNQ_HW/add.bit

User IP name:add_0

**** 2- Input definitions ****

// Input 1

Input name:a

Protocol:lite

Type:int32

Address Offset (if AXI-Lite):16

// Input 2

Input name:b

Protocol:lite

Type:int32

Address Offset (if AXI-Lite):24

**** 3- Output definitions ****

// Output 1

Output name:sum

Protocol:lite

Type:int32[1]

Address Offset (if AXI-Lite):32
```

# FOrESTの実行

config.forestファイルが完成したので、FOrESTを実行できます。forest.pyを以下のコマンドで実行します。

`python3 forest.py -t`

ツールは数分間実行され、指定したワークスペースに2つのROS2パッケージを作成してビルドします。
それらは、forest_ <プロジェクト名> fpga_node およびforest_ <プロジェクト名> interfaceと呼ばれます。

fpga_nodeパッケージには、FPGAおよびオプションのtalkerノードとlistenerノードと通信するROS2ノードが含まれ、interfaceパッケージには、msg/FpgaIn.msg（入力信号定義）およびmsg/FpgaOut.msg（出力信号定義）内のFPGAノードのメッセージ定義が含まれます。これらのパッケージ内のファイルは、templatesフォルダーにあるJinja2テンプレートファイルに基づいて作成されます。ツールを実行すると、output/　フォルダも作成されます。このフォルダには、ROS2パッケージで使用されるJinja2テンプレートの最終バージョンが保持されます。

-t（テスト）フラグはオプションであり、ROS2を介したPSとFPGAロジック間の通信をテストするために使用される2つのROS2スクリプトを生成するようにツールに指示します。

ノードは「Talker」および「Listener」と呼ばれます。Talkerノードは適切なデータ型のランダムデータをFPGAノードの入力トピック（fpga_in_topic）にPublishし、LisntenerノードはFPGAノードの出力トピック(fpga_out_topic)からSubscribeします。Talkerノード、FPGAノード、およびListenerノードを同時に実行すると、Listenerノードでいくつかの出力を確認できるます。これは、FPGAにデータを送信してFPGAから出力を受信できていることを示しています。ただし、FPGAモジュールの機能が期待どおりに動作していることを必ずしも示しているわけではありません。

 # FOrESTで生成されたROS2ノードの実行
FOrESTの実行が終了したらターミナルを3つ開き、モジュールが期待どおりに機能していることを確認します。

1つはROS2-FPGAノード用、1つはTalkerノード用、もう1つはListenerノード用です。

**注意：ROS2-FPGAノードを実行する際は、以下のコマンドでユーザをrootに変更してから実行してください。**

`sudo -sE`

- ROS2-FPGAノード：
```
cd <dev_ws location>
. install/setup.bash
ros2 run forest_simple_add_fpga_node fpga_node
```
- Talkerノード：
```
cd <dev_ws location>
. install/setup.bash
ros2 run forest_simple_add_fpga_node talker
```
- Listenerノード：
```
cd <dev_ws location>
. install/setup.bash
ros2 run forest_simple_add_fpga_node listener
```
