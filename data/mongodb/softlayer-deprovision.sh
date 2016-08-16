#!/bin/bash
# First remove the ips from our known hosts in case we get these again in the future
masterip=`slcli vs list | grep mongo1 | awk '{print $3}'`
replicanode1ip=`slcli vs list | grep mongo2 | awk '{print $3}'`
replicanode2ip=`slcli vs list | grep mongo3 | awk '{print $3}'`

# Then cancel the vms
masterid=`slcli vs list | grep elasticm1 | awk '{print $1}'`
replicanode1id=`slcli vs list | grep elasticdata1 | awk '{print $1}'`
replicanode2id=`slcli vs list | grep elasticdata2 | awk '{print $1}'`

ssh-keygen -f "/Users/rcordell/.ssh/known_hosts" -R $masterid
ssh-keygen -f "/Users/rcordell/.ssh/known_hosts" -R $replicanode1id
ssh-keygen -f "/Users/rcordell/.ssh/known_hosts" -R $replicanode2id


slcli -y vs cancel $masterid
slcli -y vs cancel $replicanode1id
slcli -y vs cancel $replicanode2id

rm sl.hosts

