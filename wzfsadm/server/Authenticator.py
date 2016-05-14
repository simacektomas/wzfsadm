import hashlib
import ConfigParser
import os.path
from app.Logger import Logger

class Authenticator:

	logger = Logger()
	AUTH_FILE = '/etc/wzfsadm/.auth_file'
	CONFIG_FILE = '/etc/wzfsadm/main.conf'	
	#-------------------------------------------------------------------------#

	def __init__( self, hash_function="sha256" ):
		

		self.hash_function = hash_function
		# Load config
		config = ConfigParser.RawConfigParser()
		config.read( self.CONFIG_FILE )
		try:
			user_database = config.get( 'auth', 'user_database' )
			if not os.path.isfile( user_database ):
				self.logger.log_error( "WARNING user_database %s does not exist. Using default %s.", user_database, self.AUTH_FILE )
			else:
				self.AUTH_FILE = user_database
			
		except ConfigParser.NoSectionError: 
			self.logger.log_error( "ERROR No section [auth] in main.conf." )
		except ConfigParser.NoOptionError: 
			self.logger.log_error( "WARNING user_database missing in main.conf. Using default %s.", self.AUTH_FILE )	

		self.auth_file = self.AUTH_FILE

	#-------------------------------------------------------------------------#

	def authenticate( self, username, password ):
	
		#try:
			auth = open( self.auth_file, 'r' )							
			for line in auth:

				tokens = line.rstrip( "\r\n" ).split(":")
				#Getting username and hash of password from auth file
				if len( tokens ) != 3:
					# Invalid format of line [ username, used hash, hash ]
					continue
				# fusername like username founded in file
				fusername, ffunction, fhash = tokens			

				if ( fusername == username ):
					# we have founded the user
					# Set hashing function to one that have been used 
					# Hashing password that we get and compare it
					h = hashlib.new( ffunction )
					h.update( password )

					if h.hexdigest() == fhash:
						# Both hashes are indentical => authenticated
						return True
					else: 
						# Hashes differ => not authenticated
						return False
				else :
					# We did not find the user
					continue 
		#except IOError as exp:

		#	print "I/O error".format( exp.errno, exp.strerror )
		#	print "Tus"
		# User is not in the file
			return False 

	#-------------------------------------------------------------------------#

	def user_add( self, username, password ):
    
        	try:
        	        with open( auth_file_path, 'r+a' ) as authFile:
        	                lines = authFile.read().splitlines()
        	                for line in lines:
        	                        tokens = line.split(":")
	
        	                        #Getting username and hash of password from auth file
        	                        usernameToCompare = tokens[0]
	
					if username == usernameToCompare:
						#User already exists
						return 1 	
				#User does not exist
				h = hashlib.new ( hashFunction ) 
				h.update( password )
				hashedPassword = h.hexdigest()
				#Create line to write into auth file	
				userLine = username+":"+hashFunction+":"+hashedPassword+"\n" 
				print userLine
				#Creating new user	
				authFile.write( userLine )

		except IOError as exp:
			print "I/O error".format( exp.errno, exp.strerror )	
		return 0 
#------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------#
