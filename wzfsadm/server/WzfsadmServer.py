import ConfigParser
import socket
import ssl
import sys
import os.path
from SocketServer import TCPServer
from SocketServer import ThreadingMixIn
from app.Logger import Logger

# Inherit from TCPServer
"""
    - server_bind()
    - server_activate()
    - get_request() -> request, client_address
    - handle_timeout()
    - verify_request(request, client_address)
    - server_close()
    - process_request(request, client_address)
    - shutdown_request(request)
    - close_request(request)
    - handle_error()
"""
class WzfsadmServer( ThreadingMixIn, TCPServer ):
	# Allow server to quickly reuse address => for testing purposes
	allow_reuse_address = 1
	#-------------------------------------------------------------------------#
	# If config file is not loaded this would be the default parameters
	# DEFAULT VALUES
	SSL = True
	CERT_FILE = "/etc/wzfsadm/ssl/cert.pem"
	KEY_FILE = "/etc/wzfsadm/ssl/key.pem"
	ADDRESS_FILTER = [
			"127.0.0.1",
			"192.168.0.104",
			"192.168.0.101"
		  ]
	CONFIG_FILE = '/etc/wzfsadm/main.conf'	
	logger = Logger()
	#-------------------------------------------------------------------------#
	def __init__( self, address, RequestHandlerClass ):
		TCPServer.__init__( self, address, RequestHandlerClass )
		# SETTING UP CONFIG VALUES	
		config = ConfigParser.RawConfigParser()
		config.read( self.CONFIG_FILE )
		# Parsing SSL section
		try:
			# GET SSL
			try:	
				self.SSL = config.getboolean( "ssl", "ssl" )

			except ConfigParser.NoOptionError: 
				self.logger.log_error( "WARNING ssl not found in main.conf. Using default ssl True." )
			except ValueError:
				self.logger.log_error( "WARNING Not valid value %s for ssl. Using default.", config.get( "ssl", "ssl" ) )
			try:	
				key_file = config.get( "ssl", "key_file" )
				if not os.path.isfile( key_file ):
					self.logger.log_error( "WARNING key_file %s does not exist. Using default %s.", key_file, self.KEY_FILE )
				else:
					self.KEY_FILE = key_file
			except ConfigParser.NoOptionError: 
				self.logger.log_error( "WARNING key_file missing in main.conf. Using default %s.", self.KEY_FILE )

			try:	
				cert_file = config.get( "ssl", "cert_file" )
				if not os.path.isfile( cert_file ):
					self.logger.log_error( "WARNING cert_file %s does not exist. Using default %s.", cert_file, self.CERT_FILE )
				else:
					self.CERT_FILE = cert_file
			except ConfigParser.NoOptionError: 
				self.logger.log_error( "WARNING cert_file missing in main.conf. Using default %s.", self.CERT_FILE )
							
		except ConfigParser.NoSectionError: 
			self.logger.log_error( "ERROR No section [ssl] in main.conf." )

		try:
			address_filter = config.get( "server", "address_filter" )
			addresses = address_filter.split( ',' )			
			flag = True
			for address in addresses:
				address = address.strip()
				try:
					socket.inet_aton( address )
				except socket.error:
					self.logger.log_error( "WARNING Bad address %s in address_filter missing in main.conf. Using default %s.", address, self.ADDRESS_FILTER )
					flag = False
					break
			if flag:
				self.ADDRESS_FILTER = addresses	
			
		except ConfigParser.NoSectionError: 
			self.logger.log_error( "ERROR No section [server] in main.conf." )
		except ConfigParser.NoOptionError: 
			self.logger.log_error( "WARNING address_filter missing in main.conf. Using default %s.", self.ADDRESS_FILTER )		
	#-------------------------------------------------------------------------#
	#Override server_bind to store the server name.
	def server_bind( self ):	
		# Call the default method and store server name	
		try:
			TCPServer.server_bind( self )
		except socket.error:
			self.logger.log_error( "ERROR Cannot bind server." )		
			sys.exit( 1 )
		host, port = self.socket.getsockname()[:2]
		self.server_name = socket.getfqdn(host)
		self.server_port = port

	#-------------------------------------------------------------------------#
	# Method to override because of SSL Connection needed
	def get_request( self ):

		if self.SSL:
			# Want to turn on SSL
			#Accept incoming connection, wrap socket to SSL socket
			connection, client_addr = self.socket.accept()
			#try:
			return ( ssl.wrap_socket( 
							  connection,
							  certfile = self.CERT_FILE,
							  keyfile = self.KEY_FILE,
							  server_side = True,
							  ssl_version = ssl.PROTOCOL_TLSv1 
							),
					 client_addr 
				       )		
			#except ssl.SSLError as err:
			#	self.logger.log_error( "SSL BAD" )
			#	return None
				
		else:
			
			return self.socket.accept()
	#-------------------------------------------------------------------------#
	# Override because we want to control IPs that can access to this server
	def verify_request( self, request, client_address ):
		# Check if ip is in allowed IPS
		address, port = client_address
		if address not in self.ADDRESS_FILTER:
			return False

		return True	
	#-------------------------------------------------------------------------#
	def process_request_thread( self, request, client_address ):
		"""Same as in BaseServer but as a thread.

		In addition, exception handling is done here.

		"""
		try:
		    self.finish_request( request, client_address )
		    self.shutdown_request( request )

		except Exception as exc:

		    self.handle_error( request, client_address, exc )
		    self.shutdown_request( request )
	
	#-------------------------------------------------------------------------#
	def handle_error( self, request, client_address, exc ):

		self.logger.log_error( "ERROR During request from %s:%s. %s", client_address[0], client_address[1], exc )		
	
