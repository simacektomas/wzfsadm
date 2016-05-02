#!/usr/bin/python -B 
import ConfigParser
import socket
from app.Logger import Logger
from server.WzfsadmServer import WzfsadmServer
from server.WzfsadmRequestHandler import WzfsadmRequestHandler



# DEFAULT VALUES
ADDRESS = '0.0.0.0'
PORT = 4443
CONFIG_FILE = '/etc/wzfsadm/main.conf'

logger = Logger()
config = ConfigParser.RawConfigParser()
config.read( CONFIG_FILE )
# GET CONFIG VALUES
try:
	try:	
		address = config.get( "server", "address" )
		try: 
			socket.inet_aton( address )
			ADDRESS = address
		except socket.error:
			logger.log_error( "WARNING Invalid value %s for address in main.conf. Using default %s.", address, ADDRESS )		

	except ConfigParser.NoOptionError: 
		logger.log_error( "WARNING No address found in main.conf. Using default %s.", ADDRESS )	
	try:
		port = config.getint( "server", "port" )
		if port > 65535:			
			logger.log_error( "WARNING Port values need to be less than 65535. Using default %s.", PORT )	
		else:
			PORT = port 
			
	except ConfigParser.NoOptionError: 
		logger.log_error( "WARNING No port found in main.conf. Using default %s.", PORT )	
	except ValueError:
		logger.log_error( "WARNING Not valid value %s in main.conf for port. Using default %s.", config.get( "server", "port" ),PORT )	
except ConfigParser.NoSectionError: 
	logger.log_error( "ERROR No section [server] in main.conf." )

server = WzfsadmServer( ( ADDRESS, PORT ), WzfsadmRequestHandler )
server.serve_forever()


