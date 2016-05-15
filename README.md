# wzfsadm

This application is web based tool for administrating ZettaByte file system. It allows administrator to monitor or administrate some basic function of ZFS.
Source codes of application are in wzfsadm/ folder. Source codes for package wzfsadm-i386.pkg are in root folder.

You can create package by command #make pkg. You have to run it in root folder. It will create file wzfsadm-i386.pkg in current directory. The whole application is instaled by command #pkgadd -d wzfsadm-i386.pkg. It will copy sources of application and create all required components. Application will run automaticly or you can run it by #svcadm enable wzfsadm.
