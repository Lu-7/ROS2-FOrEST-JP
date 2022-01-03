#import ROS python
import rclpy
from rclpy.node import Node

#import Libraries to connect with the FPGA HW
import struct
import numpy as np
from pynq import Overlay
from pynq import MMIO
from pynq import allocate
import pynq.lib.dma

from mnist_cnn_interface.msg import FpgaIn
from mnist_cnn_interface.msg import FpgaOut

class FpgaNode(Node):
  def __init__(self):
    super().__init__("fpga_node")
    self.fpga_pub = self.create_publisher(FpgaOut, "fpga_out_topic", 10)
    self.fpga_sub = self.create_subscription(FpgaIn, "fpga_in_topic", self.fpga_sub_callback, 10)
    self.fpga_sub
    
    self.init_fpga()
    self.program_fpga()
    self.setup_fpga()
  
  def init_fpga(self):
    self.bit_file = "/home/xilinx/mnist_cnn.bit"
    self.user_ip = "cnn_top_0"
    #self.in_map = {"image_in": {"protocol": "stream", "type": "int", "n_bit"}}
  
  def program_fpga(self):
    print("Downloading bit file {}...".format(self.bit_file))
    self.ovl = Overlay(self.bit_file)
    print("Bit file downloaded")
  
  def setup_fpga(self):
    regs = self.ovl.ip_dicy[self.user_ip]
    phys_addr = regs["phys_addr"]
    addr_range = regs["addr_range"]
    print("USER IP phys_addr = 0x{:X}".format(phys_addr))
    print("USER IP addr_range = {}".format(addr_range))
    
    self.mmin = MMIO(phys_addr, addr_range)
    self.dma = self.ovl.axi_dma_0
    
    self.input_buffer = allocate(shape=(784,), dtype=np.uint8)
    self.output_buffer = allocate(shape=(1,), dtype=np.uint8)
  
  def process_input(self, msg):
    data_size_in = 784
    for i in range(data_size_in):
      self.input_buffer[i] = msg[i]
  
  def process_output(self):
    data_size_out = 1
    val=[0]*data_size_out
    
    for i in range(data_size_out):
      val[i]=int(self.output_buffer[i])
    
    return val
  
  def setup_dma_buffer(self):
    self.dma.sendchannel.transfer(self.input_buffer)
    self.dma.recvchannel.transfer(self.output_buffer)
    
    return
  
  def do_calc(self):
    self.mmio.write(0x00, 1)
    if self.dma.sendchannel.running:
      self.dma.sendchannel.wait()
    if self.dma.recvchannel.running:
      self.dma.recvchannel.wait()
      
    self.wait_result()
  
  def wait_result(self):
    while(not ((self.mmio.read(0x00) >> 1) & 0x0001)):
      continue
  
  def fpga_pub_callback(self):
    msg = FpgaOut()
    msg.digit = self.process_output("digit")
    self.fpga_pub.publish(msg)
    
  def fpga_sub_callback(self, msg):
    self.process_input(msg.image_in)
    self.setup_dma_buffers()
    self.do_calc()
    self.fpga_pub_callback()
    
def main(args=None):
  rclpy.init(args=args)
  
  fpga_node = FpgaNode()
  rclpy.spin(fpga_node)
  
  fpga_node.destroy_node()
  rclpy.shutdown()

if __name__=="__main__":
  main()
