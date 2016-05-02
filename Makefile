PKG=wzfsadm
PKGFILE=$(PKG)-i386.pkg

pkg:
	pkgmk -o -d /tmp 
	touch $(PKGFILE)
	pkgtrans -s /tmp $(PKGFILE) $(PKG) 
	rm -r /tmp/$(PKG)
