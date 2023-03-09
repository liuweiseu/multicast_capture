#! /home/wei/.conda/envs/seti/bin/python
from MulticastPacketCapture import MulticastReceiver

def main():
    # nic_name = 'enp3s0'
    local_ip = '192.168.1.100'
    mc_ip = "239.1.0.3"
    mc_port = 12345
    mr = MulticastReceiver(local_ip, mc_ip, mc_port)
    # receive multicast packets
    print('receiving multicast packets...')
    mr.receive(save=True)
    # plot multicast packets
    print('plotting data...')
    mr.plotting()
    print('done.')

if __name__ == '__main__':
    main()