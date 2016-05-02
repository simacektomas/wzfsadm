#!/bin/bash
############################################################
# Description:
#
# Args 
#	$1: path to file sources
#
# Autor: Tomas Simacek (simactom)
############################################################

if [ $# -lt 1 ]
then
	echo "Usage : $0 path"
        exit 1
fi

DISKS="`/usr/wzfsadm/app/model/modules/PoolModule/shell/listdisk.sh`"
FILES="`/usr/wzfsadm/app/model/modules/PoolModule/shell/listfiles.sh $1`"

echo "$DISKS"
echo "$FILES"

