import subprocess
import json

class Pool:
	
	# How many spaces are used for one nested block of configuration line		
	SPACES = 2
	#-------------------------------------------------------------------------#

	def __init__( self, zpool_name ):
		# Construct zpool by name
		self.zpool_name = zpool_name		
		# Main part of zpool class, this dictionary is for storing real data
		self.zpool_properties = dict()
		# Initialize config array
		self.zpool_properties["config"] = []

		# Try to get zpool status
		
		if not ( self.get_zpool_status() and self.get_zpool_properties() and
			 self.parse_zpool_status() and self.parse_properties() ) :
			# Zpool name probably doesn't exist
			raise ValueError 
	#-------------------------------------------------------------------------#

	def get_zpool_status( self ):	
		# Get zpool status for zpool name
		process = subprocess.Popen( [ "/usr/sbin/zpool", "status", self.zpool_name ],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )

		self.zpool_status, stderr = process.communicate()

		if process.returncode != 0:
			# Zpool name probably doesn't exist
			return False

		return True

	#-------------------------------------------------------------------------#

	def get_zpool_properties( self ):
		# Get all properties of zpool
		process = subprocess.Popen( [ "/usr/sbin/zpool", "get", "all", self.zpool_name ],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )

		self.zpool_get_all, stderr = process.communicate()

		if process.returncode != 0:
			# Zpool name probably doesn't exist
			return False

		return True

	#-------------------------------------------------------------------------#
	
	def parse_zpool_status ( self ):
	
		zpool_configuration = []		
		zpool_property = ''

		lines = self.zpool_status.splitlines()
		for line in lines:
			# Empty line
			if line == '': continue 

			tokens = line.split(':')
			zpool_property = tokens[0].strip()

			if len( tokens ) >= 2:
				# Line should look like property: value
				zpool_property = tokens[0].strip()
				zpool_property_value = tokens[1].strip()
				
				if zpool_property == "config":
					zpool_property_value = []
				# Add zpool property with value
				self.zpool_properties.update( 
								{ zpool_property:zpool_property_value } 
							    )
				prev_property = zpool_property

			elif prev_property != 'config':
				# No property name on this line => just one token => previous property is not config
				# it means that this line belong to previous property
				zpool_property_value = tokens[0].strip()
				self.zpool_properties[ prev_property ] += " " + zpool_property_value

			else:
				# Previous property was config => this line is part of zpool configuration
				config_line = tokens[0].strip('\t')
				zpool_configuration.append( config_line )

		if not self.parse_configuration( zpool_configuration ):
			return False

		return True

	#-------------------------------------------------------------------------#
		
	def parse_configuration( self, zpool_configuration ):
		#, zpoolConfiguration, zpool

		config_stack = []
		
		# No configuration readed
		if len( zpool_configuration ) == 0 :
			return False
		# First line have to be title line
		if zpool_configuration[0].split() != [ "NAME", "STATE","READ","WRITE","CKSUM" ]:
			return False
		# Get rid off label
		zpool_configuration.pop(0)			

		keys = [ "name","state",'read','write','cksum' ] 
		for line in zpool_configuration:			
			# Get how much is line nested
			cur_nested = Pool.indentation( line )/ self.SPACES

			# Root node, cache, log, zpool
			if cur_nested == 0:
				# If there is vdev on stack
				if config_stack:
					while len( config_stack ) > 1:
						# Get son of parent
						son = config_stack.pop()
						parent = config_stack[-1]
						parent["config"].append( son )

					config_stack = []

				# Get properties from line				
				properties = line.split()
				# Create new virtual device from line
				root_device = dict( zip( keys, properties ) )
				# Init config
				root_device["config"] = []
				# Push device to config and stack
				self.zpool_properties["config"].append( root_device )
				config_stack.append( root_device )
				# Set indentation
				prev_nested = cur_nested			
				continue

			# This node is son of previous
			if cur_nested > prev_nested:
				# Just default action 
				pass
			# The previous node and this node are siblings			
			if cur_nested == prev_nested:
				# Get previous sibling out of stack 
				sibling = config_stack.pop()
				# Get reference to parent
				parent = config_stack[-1]
				# and put it to parent
				parent["config"].append( sibling )
				
			# We are nesting out ouf vdevice so we have to close it
			if cur_nested < prev_nested:

				son = config_stack.pop()
				parent = config_stack[-1]
				parent["config"].append( son )
			
				parent = config_stack.pop()
				parent_of_parent = config_stack[-1]
				parent_of_parent["config"].append( parent )			
			# DEFAULT
			# Get properties from line
			properties = line.split()
			# Create new virtual device from line
			v_device = dict( zip( keys, properties ) )
			# Init config
			v_device["config"] = []
			# Push device to stack
			config_stack.append( v_device )

			prev_nested = cur_nested

		while len( config_stack ) > 1:
			# Get son of parent
			son = config_stack.pop()
			parent = config_stack[-1]
			parent["config"].append( son )				

		return True

	#-------------------------------------------------------------------------#

	def parse_properties( self ):
		
		properties = self.zpool_get_all.splitlines()
		
		if len( properties ) == 0:
			return False

		if properties[0].split() != [ "NAME", "PROPERTY", "VALUE", "SOURCE"]:
			return False

		properties.pop(0)

		for line in properties:
			try:
				# Get properties and their values
				zpool_name, zpool_property, property_value, source = line.split()
				self.zpool_properties.update(
								{ zpool_property:property_value.rstrip("%") }
							    )
			except ValueError:
				# Not valid format of input ( zpool get all pool ) 
				return False
		return True
		
	#-------------------------------------------------------------------------#
	#-------------------------------------------------------------------------#
	@staticmethod
	def indentation ( string ):
		indentation=0
		for c in string:
			if c != ' ': return indentation
			else: indentation += 1
	#-------------------------------------------------------------------------#
	def get_properties( self ):
		return self.zpool_properties
	#-------------------------------------------------------------------------#
