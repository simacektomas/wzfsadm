#!/bin/bash
############################################################
# Description:
#
# Args:
#
# Autor: Tomas Simacek (simactom)
############################################################
INPUT=`/usr/sbin/format < /dev/null | sed '/^Searching for/d;/^Specify disk/d' | awk 'NR > 3' `
function diskspace {
	# Print out size of given device
	[ $# -lt 1 ] && exit 1
	fdisk -G $1 | tail -1 | awk '{
		ncyl=$2
		nhead=$5
		nsect=$6
		secsz=$7
		sectors=ncyl*nhead*nsect;
		bytes=sectors/(1024/secsz);
		printf("%0.2f", bytes*1024/1000/1000/1000 );
	}'
}
# Parsing disks individually
while read -r NUMBER LOGICAL COMERCIAL
do
	# Read system name
	read -r SYSTEM	
	# Partition number default 1
	PART_NUM=0
	STATUS="free"
	# Check if there is some FS on the disk
	fstyp "/dev/dsk/${LOGICAL}p0" &> /dev/null
	[[ $? == 0 ]] && STATUS="used"

	#SIZE="`diskspace /dev/rdsk/${LOGICAL}p0 2> /dev/null`GB"
	#[[ $SIZE == "GB" ]] && SIZE="-"
	echo "${LOGICAL} disk $STATUS"

	# For each disk read disk table to get parition 
	DISK_TABLE=`/usr/sbin/fdisk -W - /dev/rdsk/${LOGICAL}p0 | sed '/^\*/d;/^$/d'`
	
	# Cannot read disk table for current disk
	[[ $? != "0" ]] && continue
	while read -a PARTITON
	do
		PART_NUM=$(( $PART_NUM + 1 ))			

		STATUS="free"		
		# There is no partition
		[[ ${PARTITON[0]} == "0" ]] && continue
		# Check if there is some FS on the partition
		fstyp "/dev/dsk/${LOGICAL}p${PART_NUM}" &> /dev/null
		[[ $? == 0 ]] && STATUS="used"

		echo "${LOGICAL}p${PART_NUM} partition $STATUS"

		# Increment part_num
		
		
	done <<< "$DISK_TABLE"

done <<< "$INPUT"
