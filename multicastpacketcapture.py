#! /usr/bin/env python
import sys
import struct
import time
import socket
import numpy as np
from datetime import datetime
try:
    import matplotlib.pyplot as plt
except:
    pass
import scipy.fftpack as fftpack
from argparse import ArgumentParser

MCAST_GROUP_IP = "239.1.0.3"
LOCAL_IP = '192.168.1.100'
MCAST_GROUP_PORT = 12345
FRAME_LEN = 4104
METADATA_LEN = 8
DATA_LEN = FRAME_LEN - METADATA_LEN
FS=1000
class MulticastReceiver(object):
    def __init__(self, local_ip = LOCAL_IP, mcg_ip=MCAST_GROUP_IP, mcg_port=MCAST_GROUP_PORT):
        self.mcg_ip = mcg_ip
        self.local_ip = local_ip
        self.mcg_port = mcg_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.mcg_ip, self.mcg_port))
        mreq = socket.inet_aton(self.mcg_ip) + socket.inet_aton(self.local_ip)
        self.sock.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,mreq)
        self.metadata = np.zeros(FRAME_LEN,dtype=np.int8)
        self.data = np.zeros(DATA_LEN,dtype=np.int8)

    def receive(self, pkts=FRAME_LEN, save=False, index=0):
        d, addr = self.sock.recvfrom(pkts)
        metadata = struct.unpack('%db'%METADATA_LEN, d[0:8])
        data = struct.unpack('%db'%DATA_LEN, d[8:])
        self.metadata = np.array(metadata)
        self.data = np.array(data)
        if save:
            np.savez('adc_data_pol%d.npz'%index,metadata=self.metadata,data=self.data)
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
    freq = np.arange(0,fs,df)
    data_fft = fftpack.fft(data)
    l = len(freq)
    sub2 = fig.add_subplot(3,tcol,ind[2])
    sub2.plot(freq[0:int(l/2)],np.log10(np.abs(data_fft[0:int(l/2)])),color='blue')
    sub2.set_title('Power Spectrum', color='blue')
    sub2.set_xlabel('Freq(MHz)')
    sub2.set_ylabel('Power(dB)')
    # ready to go
    fig.tight_layout()


def main():
    local_ip = '192.168.1.100'
    mc_ip = "239.1.0.3"
    mc_port = 12345
    parser = ArgumentParser(description='Check adc data from a multicast receiver.')
    parser.add_argument('--lip0', type=str, dest='lip0', help='local ip address of pol0.')
    parser.add_argument('--mip0', type=str, dest='mip0', help='multicast group ip address of pol0.')
    parser.add_argument('--lip1', type=str, dest='lip1', help='local ip address of pol1.')
    parser.add_argument('--mip1', type=str, dest='mip1', help='multicast group ip address of pol1.')
    parser.add_argument('--mport', type=int, dest='mport',default=12345,help='multicast port.')
    parser.add_argument('--save', dest='save', default=False, action='store_true', help='save data to file.')
    parser.add_argument('--show', dest='show', default=False, action='store_true' ,help='show the plot.')
    parser.add_argument('--savefig', dest='savefig', default=False, action='store_true' ,help='save the figure.')
    args = parser.parse_args()
    ds = 0
    data = np.zeros(2, dtype=object)
    print('****************************************')
    if args.lip0 is not None and args.mip0 is not None:
        mr = MulticastReceiver(args.lip0, args.mip0, args.mport)
        print('receiving multicast packets from pol0...')
        d,m = mr.receive(save=args.save,index=0)
        data[0] = d
        ds = ds + 1

    if args.lip1 is not None and args.mip1 is not None:
        mr = MulticastReceiver(args.lip1, args.mip1, args.mport)
        print('receiving multicast packets from pol1...')
        d,m = mr.receive(save=args.save,index=1)
        data[1] = d
        ds = ds + 1
    print('****************************************')
    for i in range(len(data)):
        if(type(data[i])!=int):
            print('Pol%d -  Mean: %.2f; RMS: %.2f'%(i, np.mean(data[i]),np.std(data[i])))

    if args.show or args.savefig:
        fig = plt.figure()
        j = 0
        for i in range(len(data)):
            if(type(data[i])!=int):
                plotting(fig,data[i],ds,j)
                j = j + 1
        if args.savefig:
            print('saving figure...')
            # save the fig
            t = datetime.now()
            t_str = datetime.strftime(t, '%Y-%m-%d-%H-%M-%S-%f')
            fig.savefig(t_str+'.png',dpi=300)
        if args.show:
            print('plotting data...')
            plt.show()
        plt.close('all')
    print('done.')
    print('****************************************')

if __name__ == '__main__':
    main()
