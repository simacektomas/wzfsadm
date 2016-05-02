#!/bin/bash
############################################################
# Description:
#	Prints out files that can be used as source for ZFS
#	in format FILEPATH SIZE
# Args:
#	$1:
#		path where to search for files
# Return value:
#	0
#	1
#	2
#
# Autor: Tomas Simacek (simactom)
############################################################
if [ $# -lt 1 ]
then
	echo "Usage : $0 path"
        exit
fi
#----------------------------------------------------------#
FILES_PATH="$1"
TOPARSE="`ls -lh $1 2> /dev/null`" 
# Directory probably does not exist
[ $? -ne 0 ] && exit 1

# Total block used 
read -r TOTAL VALUE <<< "$TOPARSE"
# Check if directory is empty if so, exit
[ "$VALUE" == 0  ] && exit 2
#Delete first line from input
FILES="`echo "$TOPARSE" |awk 'NR > 1'`"

#Parse input, determine absolute path and print out
while read -ra ARRAY 
do
	ABS_PATH="`realpath "${FILES_PATH}/${ARRAY[8]}"`"
	STATUS="free"

	# Check if file is avalible to create FS on 
	fstyp "$ABS_PATH" &> /dev/null
	[ $? -eq 0 ] &&	STATUS="used"
	echo "${ABS_PATH} file $STATUS"

done <<< "$FILES"

exit 0
