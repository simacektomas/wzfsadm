import re
import ConfigParser
from app.Logger import Logger
# Base class from which every module class have to inherit
class BaseModuleClass:
	#-------------------------------------------------------------------------#
	SAFE_MODE = True
	CONFIG_FILE = '/etc/wzfsadm/main.conf'
	logger = Logger()
	#-------------------------------------------------------------------------#
	def __init__( self, name ):

		self.name = name		
		
		config = ConfigParser.RawConfigParser()
		config.read( self.CONFIG_FILE )
		
		try:
			self.SAFE_MODE = config.getboolean( "app", "safe_mode" )

		except ValueError:
			self.logger.log_error( "WARNING Not valid value %s for safe_mode. Using default safemode on.", config.get( "app", "safe_mode" ) )
		except ConfigParser.NoSectionError: 
			self.logger.log_error( "ERROR No section [app] in main.conf. Using default safemode on." )
		except ConfigParser.NoOptionError: 
			self.logger.log_error( "WARNING safe_mode missing in main.conf. Using default safe_mode on." )

		self.expr = re.compile( '^rpool' )

	#-------------------------------------------------------------------------#
	def init_module( self ):		
		pass
	#-------------------------------------------------------------------------#
