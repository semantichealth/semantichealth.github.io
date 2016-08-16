#!/bin/bash
# First remove the ips from our known hosts in case we get these again in the future
masterip=`slcli vs list | grep data06 | awk '{print $3}'`
datanode1ip=`slcli vs list | grep data07 | awk '{print $3}'`
datanode2ip=`slcli vs list | grep data08 | awk '{print $3}'`

# Then cancel the vms
masterid=`slcli vs list | grep data06 | awk '{print $1}'`
datanode1id=`slcli vs list | grep data07 | awk '{print $1}'`
datanode2id=`slcli vs list | grep data08 | awk '{print $1}'`

echo "Removing known_hosts entries"
ssh-keygen -R $masterip
ssh-keygen -R $datanode1ip
ssh-keygen -R $datanode2ip

echo "Cancelling SoftLayer VMs..."
slcli -y vs cancel $masterid
slcli -y vs cancel $datanode1id
slcli -y vs cancel $datanode2id

echo "Cleaning up sl.hosts file..."
rm sl.hosts

