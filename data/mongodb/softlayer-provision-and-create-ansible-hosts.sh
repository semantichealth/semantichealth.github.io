#!/bin/bash
slcli -y vs create --datacenter=sjc03 --hostname=mongo1 --domain=w210.rlc --billing=hourly --key=rcordell --cpu=2 --memory=8196 --disk=100 --network=1000 --os=CENTOS_LATEST_7
sleep 5
slcli -y vs create --datacenter=sjc03 --hostname=mongo2 --domain=w210.rlc --billing=hourly --key=rcordell --cpu=2 --memory=8196 --disk=100 --network=1000 --os=CENTOS_LATEST_7
sleep 5
slcli -y vs create --datacenter=sjc03 --hostname=mongo3 --domain=w210.rlc --billing=hourly --key=rcordell --cpu=2 --memory=8196 --disk=100 --network=1000 --os=CENTOS_LATEST_7

# Wait for softlayer to issue ips to the servers we just created
sleep 300

# Grab the ip addresses
masterip=`slcli vs list | grep mongo1 | awk '{print $3}'`
replica1ip=`slcli vs list | grep mongo2 | awk '{print $3}'`
replica2ip=`slcli vs list | grep mongo3 | awk '{print $3}'`

REPLICANODES=($replica1ip $replica2ip)
ALLNODES=($masterip ${REPLICANODES[@]})

# cloud image specific configuration
user=root

# Generate ansible hosts file ##################################################
hostsfile=sl.hosts

echo "[master]" >> $hostsfile
echo "$masterip host_alias=mongo1" >> $hostsfile
hostnum=2
echo "[replicanodes]" >> $hostsfile
for replicanodeip in "${REPLICANODES[@]}"
do
  echo "$replicanodeip host_alias=mongo$hostnum"  >> $hostsfile
  let hostnum+=1
done

ansible -i sl.hosts all -u root -m ping

# Generate an /etc/hosts file ##################################################
#moved to ansible
#etchostsfile=etc.hosts
#echo "$masterip benchmaster" > $etchostsfile
#hostnum=1
#for slaveip in "${SLAVES[@]}"
#do
#  echo "$slaveip benchslave$hostnum" >> $etchostsfile
#  let hostnum+=1
#done

# Send update to the /etc/hosts file
#for nodeip in "${ALLNODES[@]}"
#do
#  cat $etchostsfile | ssh $user@$nodeip "cat >> /etc/hosts"
#done

# Set up the hosts to be able to communicate with each other ###################
# Note: this has been moved to the ansible playbook
#keyfilename=`cat /dev/urandom | base64 | head -c 8`
#ssh-keygen -t rsa -q -f temp-$keyfilename.key -N ''
#for nodeip in "${ALLNODES[@]}"
#do
#  ssh $user@$nodeip "mkdir -p ~/.ssh"
#  cat temp-$keyfilename.key | ssh $user@$nodeip "cat > ~/.ssh/id_rsa"
#  ssh $user@$nodeip "chmod 600 ~/.ssh/id_rsa"
#  cat temp-$keyfilename.key.pub | ssh $user@$nodeip "cat >> ~/.ssh/authorized_keys"
#done
#rm temp-$keyfilename.key
#rm temp-$keyfilename.key.pub
