import sys
from time import strftime, gmtime
class Logger():	

	#-------------------------------------------------------------------------#
	def log_error( self, format, *args ):
		sys.stderr.write( "[ %s %s ]\n" %
				( self.get_current_time(),
				  format % args ))
	#-------------------------------------------------------------------------#
	def log_message( self, format, *args ):
		sys.stdout.write( "[ %s %s ]\n" %
				( self.get_current_time(),
				  format % args ))
	#-------------------------------------------------------------------------#
	def get_current_time( self ):
		# Return current time
		return strftime( "%B %d %H:%M:%S", gmtime())
