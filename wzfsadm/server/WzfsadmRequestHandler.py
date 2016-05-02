from Authenticator import Authenticator
from app.App import App

import BaseHTTPServer
import socket
import urllib
import urlparse
import os
import sys
import mimetypes

# This class inherit from BaseHTTPRequestHandler
class WzfsadmRequestHandler( BaseHTTPServer.BaseHTTPRequestHandler ):

	AUTH = True
	# Where the server should look after files
	DOCUMENT_ROOT = "/usr/wzfsadm/web"
	#-------------------------------------------------------------------------#
	# We need to override this method to add Basic Auth function from HTTP protocol
	def handle_one_request(self):
   
		try:
			# Check if request line is not too long
			self.raw_requestline = self.rfile.readline( 65537 )
			if len( self.raw_requestline ) > 65536:

				self.requestline = ''
				self.request_version = ''
		        	self.command = ''
				# 414 Uri too long
		        	self.send_error( 414 )
		      		return

		    	if not self.raw_requestline:
				# Invalid request, no request
		      		self.close_connection = 1
		        	return
			# Check for valid request and headers
		    	if not self.parse_request():
		       		# An error code has been sent, just exit
		        	return
			# Check for valit AUTH
			if not self.process_headers():
		       		# An error code has been sent, just exit
				return

		    	mname = 'do_' + self.command
		    	if not hasattr(self, mname):

		        	self.send_error( 501, "Unsupported method (%r)" % self.command )
		        	return

		   	method = getattr(self, mname)
		    	method()
		    	self.wfile.flush() #actually send the response if not already done.
		except socket.timeout, e:
			#a read or a write timed out.  Discard this connection
			self.log_error( "Request timed out: %r", e )
			self.close_connection = 1
			return
	#-------------------------------------------------------------------------#
	# Look to received headers to find out if client authenticate themself
	def process_headers( self ):
		# If authentization is enabled
		if self.AUTH:
			# Check if client send authorization headder
			authorization_header = self.headers.get( 'Authorization', "" )
			# Client did not send any Authorization header => Unauthorized
			if not authorization_header:
				# Send response 401 => Unauthorized
				self.send_error( 401 )
				return False
			else: 
				# Client sent the Authorization header => we have to validate											
				try:
					# Authorization format "Basic (username:password).encode("base64")"
					auth_type, encoded_credentials = authorization_header.lstrip( "Authorization: " ).split(' ')
					credentials = encoded_credentials.decode( "base64" )
					# format username:password
					username, password = credentials.split( ":" )	
					authenticator = Authenticator()

					if not authenticator.authenticate( username, password ):
						# Not valid credentials
						self.send_error( 401 )						
						return False
					# Valid credentials					
			
				except ValueError:
					# Client did not send valid format of credentials
					self.send_error( 401 )
					return False

		return True
	#-------------------------------------------------------------------------#
	def send_response(self, code, message = None ):
  
        	self.log_request( code )
        	if message is None:

		   	if code in self.responses:
		        	message = self.responses[code][0]
		    	else:
		                message = ''

		if self.request_version != 'HTTP/0.9':

			self.wfile.write("%s %d %s\r\n" % ( self.protocol_version, code, message ))

		# Default headers that will be in each response
		self.send_header( 'Server', self.version_string() )
		self.send_header( 'Date', self.date_time_string() )
		# This header need to be added because of basic auth
		if self.AUTH:

			self.send_header( 'WWW-Authenticate', 'Basic realm="Secure Content"' )

	#-------------------------------------------------------------------------#
	def do_GET( self ):
		# Take care about URL	
		# Separate query string from path
		path, separator, query = self.path.partition( "?" )
		# Decode url path
		unquoted_path = urllib.unquote_plus( path )

		if query:
			# Parse and decode query string to dictionary, second parameter 
			# tell to parse blank strings
			query = urlparse.parse_qs( query, True )
		

		# Check if client request is on file
		# We don't allow to list directory only to list files like 
		# .js .css .font ..
		if os.path.isfile( self.DOCUMENT_ROOT + path ):
			# File exist, guess his type
			# Initialize mimetypes, read system default
			if not mimetypes.inited:			
				mimetypes.init()
			# Guess type for requested file by url path
			mime_type, encoding = mimetypes.guess_type( path )
			if not mime_type:
				# Default mime for files
				mime_type = "text/plain"
			try:
				f = open( self.DOCUMENT_ROOT + path, "r" )
				content = f.read()
				self.send_response( 200 )
				self.send_header( "Content-Type", mime_type )
				self.send_header( "Content-Length", len( content ) )
				self.end_headers()
				self.wfile.write( content )
			except:
				self.send_error( 404 )
			finally:
				f.close()
			return
		# It is not a file => run application
		application = App( unquoted_path, query )
		# Route request to apropriate controller
		application.route()
		# If not good response send error
		if not application.get_code() == 200:
			self.send_error( application.get_code() )			
			return

		# Response code is 200
		response = application.get_response()
		self.send_response( 200 )
		self.send_header( "Content-Type", response[1] )
		self.send_header( "Content-Length", len( response[0] ) )
		self.end_headers()
		self.wfile.write( response[0] )			
	#-------------------------------------------------------------------------#
	def log_message(self, format, *args):
       
	        sys.stdout.write("%s - - [%s] %s\n" %
                         (self.client_address[0],
                          self.log_date_time_string(),
                          format%args))

