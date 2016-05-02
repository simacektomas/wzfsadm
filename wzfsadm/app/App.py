from importlib import import_module
# Main application class that handle routing to each controller
class App:
	#-------------------------------------------------------------------------#
	def __init__( self, url, query ):
		
		self.query = query
		# Split url we need to get controller and method
		self.url = url.strip( "/" ).split( "/" )
		if self.url == [ "" ]:
			self.url.pop(0)
		# Default controller and method
		self.controller = "Dashboard"
		self.method = "index" 
		# Default content and type
		self.response_code = 200
		self.response = ( "", "text/plain" ) # Tuple ( content, type )
		
	#-------------------------------------------------------------------------#
	# Route the request to apropriate controller
	# URL protocol://host:port/controller/method
	def route( self ):
		# We have first parameter of url that is controller and it is not empty
		if len( self.url ) > 0 and self.url[0]:
			self.controller = self.url[0].lower().title()
			self.url.pop(0)
		# Controller sent or DEFAULT
		# Looking for method to call

		if len( self.url ) > 0 and self.url[0]:
			self.method = self.url[0].lower()
			self.url.pop(0)	

		# Some other argument in url => not found
		if len( self.url ):
			self.response_code = 404
			return
			
		# We call controller of the aplication that will handle the request
		module = ( "app.controllers.%sController" % ( self.controller ) )
		self.controller = ( "%sController" % ( self.controller ) )
		try:
			# Look after controller class in module
			loaded_module = import_module( module )

			reload( loaded_module )

			Class = getattr( loaded_module , self.controller )
			controller = Class( self )
			# Look after method to call
			function = getattr( controller, self.method )
			###################CALL CONTROLLER MEHOD###################
			function( self.query )
			# To set response and code
			controller.finish()
			######################################################
		except ImportError as err:
			print err
			# Controller or method cannot be instantiate or called
			self.response_code = 404
			return

		except AttributeError as err:
			print err
			self.response_code = 404
			return
	#-------------------------------------------------------------------------#
	#-------------------------------------------------------------------------#
	def get_code( self ):
		return self.response_code
	#-------------------------------------------------------------------------#
	def get_response( self ):
		return self.response
	#-------------------------------------------------------------------------#
	def set_code( self, code ):
		self.response_code = code
	#-------------------------------------------------------------------------#
	def set_response( self, response ):
		self.response = response
	#-------------------------------------------------------------------------#
	#-------------------------------------------------------------------------#

