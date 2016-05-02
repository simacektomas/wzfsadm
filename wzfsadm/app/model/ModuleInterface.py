from importlib import import_module

class ModuleInterface():
	#-------------------------------------------------------------------------#
	MODULES = "app.model.modules"
	#-------------------------------------------------------------------------#
	def __init__( self ):
		pass
	#-------------------------------------------------------------------------#
	# Look after method in specified module and return function
	def load_module( self, module_name ):
		# Convence
		# module package name will be nameModule
		# module sourcefile name will be name nameSource
		# module class name will be module_nameClass
			
		module = ( "%sModule" % ( module_name ) ) 
		module_source = ( "%sSource" % ( module_name ) )
		module_class = ( "%sClass" % ( module_name ) )
		# Load module to enviroment ( reload )
		loaded_module = self._load_module( module , module_source )

		if not loaded_module:
			# Modul cannot be loaded
			return None

		try: 
			# Check if module have the right class
			Class = getattr( loaded_module , module_class )
			# Instantiate module class
			module_class = Class()	
			##
			# All module classes have to inherite from BaseModule
			# Call module_init
			##
			module_class.init_module()
			# Get reference to function that caller wants
			return module_class	

		except AttributeError as err:		
			print str(err)
			# Module do not contain attribute ( class ) of the module name
			# or do no contatin the function to call
			
			return None
		# Function is not callable
		return None	
	#-------------------------------------------------------------------------#
	# Look after module in predefined path
	def _load_module( self, module, source ):
		# The module have to be in package of the same name and module class
		# have to have the same name too
		# modules/
		# 	ZpoolPackage/
		#		__init__.py
		#		ZpoolModule.py ( contain ZpoolClass: )
		# 	DatasetPackage/
		#		__init__.py
		#		DatasetModule.py ( contain DatasetClass: )				
		try:
			# Try to load module
			imported_module = import_module( ( "%s.%s.%s" % (
								  self.MODULES,
								  module,
								  source
							        ) 
					      ) )
			# Reload a module if changed
			reload( imported_module )	
		except ImportError as err:
			print err
			# Module cannot be load
			return None

		return imported_module
