#! /bin/bash

beam=0
eth0=enp216s0f0
eth1=enp216s0f1

local_ip0=`ifconfig ${eth0} | awk '/inet/ {print $2}' | cut -f2 -d ":"`
local_ip1=`ifconfig ${eth1} | awk '/inet/ {print $2}' | cut -f2 -d ":"`
mc_ip0='239.1.'$beam'.3'
mc_ip1='239.1.'$beam'.4'

#echo ${local_ip0}
#echo ${local_ip1}
#echo ${mc_ip0}
#echo ${mc_ip1}

./MulticastPacketCapture.py --lip0 ${local_ip0} --mip0 ${mc_ip0} --lip1 ${local_ip1} --mip1 ${mc_ip1} $1 $2