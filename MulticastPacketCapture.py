#! /usr/bin/env python
import sys
import struct
import time
import socket
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack as fftpack

MCAST_GROUP_IP = "239.1.0.3"
LOCAL_IP = '192.168.1.100'
MCAST_GROUP_PORT = 12345
FRAME_LEN = 4104
METADATA_LEN = 8
DATA_LEN = FRAME_LEN - METADATA_LEN
FS=1000
class MulticastReceiver(object):
    def __init__(self, local_ip = LOCAL_IP, mcg_ip=MCAST_GROUP_IP, mcg_port=MCAST_GROUP_PORT, fs=FS):
        # self.nic = (nic+'\0').encode('utf-8')
        self.mcg_ip = mcg_ip
        self.local_ip = local_ip
        self.mcg_port = mcg_port
        self.fs = fs
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.setsockopt(socket.SOL_SOCKET, 25, self.nic)
        self.sock.bind((self.mcg_ip, self.mcg_port))
        # mreq = struct.pack('4sl', socket.inet_aton(self.mcg_ip), socket.INADDR_ANY)
        mreq = socket.inet_aton(self.mcg_ip) + socket.inet_aton(self.local_ip)
        self.sock.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,mreq)
        self.metadata = np.zeros(FRAME_LEN,dtype=np.int8)
        self.data = np.zeros(DATA_LEN,dtype=np.int8)

    def receive(self, pkts=FRAME_LEN, save=False):
        d, addr = self.sock.recvfrom(pkts)
        metadata = struct.unpack('%db'%METADATA_LEN, d[0:8])
        data = struct.unpack('%db'%DATA_LEN, d[8:])
        self.metadata = np.array(metadata)
        self.data = np.array(data)
        if save:
            np.savez('adc_data.npz',metadata=self.metadata,data=self.data)
        return self.data, self.metadata 
    
def plotting(fig,data,tcol=1,col=0,fs=1000.0):
    rms = np.std(data)
    mean = np.mean(data)
    ind = np.arange(col,3*tcol,tcol) + 1
    # plot histogram
    sub0 = fig.add_subplot(3,tcol,ind[0])
    sub0.hist(data,bins=np.arange(-128,128),color='red')
    sub0.set_title('MEAN: %.2f RMS: %.2f'%(mean,rms), color='red')
    # plot time series
    sub1 = fig.add_subplot(3,tcol,ind[1])
    sub1.plot(data,color='green')
    sub1.set_title('Time Domain Data',color='green')
    # plot power spectrum
    df = fs/data.shape[0]
    print(df)
    freq = np.arange(0,fs,df)
    data_fft = fftpack.fft(data)
    sub2 = fig.add_subplot(3,tcol,ind[2])
    sub2.plot(freq,np.log10(np.abs(data_fft)),color='blue')
    sub2.set_title('Power Spectrum', color='blue')
    sub2.set_xlabel('Freq(MHz)')
    sub2.set_ylabel('Power(dB)')
    # ready to go
    fig.tight_layout()


def main():
    local_ip = '192.168.1.100'
    mc_ip = "239.1.0.3"
    mc_port = 12345
    mr = MulticastReceiver(local_ip, mc_ip, mc_port)
    # receive multicast packets
    print('receiving multicast packets...')
    data,metadata = mr.receive(save=True)
    # plot multicast packets
    print('plotting data...')
    fig = plt.figure()
    plotting(fig,data,2,0)
    plotting(fig,data,2,1)
    plt.show()
    print('done.')

if __name__ == '__main__':
    main()