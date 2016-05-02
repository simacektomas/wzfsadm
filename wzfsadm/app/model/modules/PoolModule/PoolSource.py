import Pool
reload(Pool)
from Pool import Pool

import re
import time
import json
import os.path
import ConfigParser
import subprocess
from app.Logger import Logger
from app.model.modules.BaseModuleClass import BaseModuleClass
################################################################################
# Module for API
# each function should return tuple ( status_of_operation, data )
#
################################################################################
class PoolClass( BaseModuleClass ):
	#-------------------------------------------------------------------------#
	MODULE_NAME = "Pool Module"
	FILE_SOURCES = "/var/wzfsadm/sources/"
	MODULE_CONFIG_FILE = "/etc/wzfsadm/poolmodule.conf"
	logger = Logger()
	#-------------------------------------------------------------------------#
	def __init__( self ):
		# Call parent constructor
		BaseModuleClass.__init__( self, self.MODULE_NAME )
	#-------------------------------------------------------------------------#
	# Inherited from base module
	def init_module( self ):

		config = ConfigParser.RawConfigParser()
		config.read( self.MODULE_CONFIG_FILE )
		
		try:
			file_sources = config.get( 'sources', 'file_sources' )
			if not os.path.isdir( file_sources ):
				self.logger.log_error( "WARNING file_sources directory %s does not exist. Using default %s.", file_sources, self.FILE_SOURCES )
			else:
				FILE_SOURCES = file_sources

		except ConfigParser.NoSectionError: 
			self.logger.log_error( "ERROR No section [sources] in poolmodule.conf." )
		except ConfigParser.NoOptionError: 
			self.logger.log_error( "WARNING file_sources missing in poolmodule.conf. Using default %s.", self.FILE_SOURCES )	
		
		
	#-------------------------------------------------------------------------#
	def list_zpool_names( self ):
		
		response = {}
		response["response"] = "Default response"

		# Get all zpools on this machine
		title_line = [ "NAME", "SIZE", "ALLOC", "FREE", "CAP", "DEDUP", "HEALTH", "ALTROOT" ]

		process = subprocess.Popen( [ '/usr/sbin/zpool', 'list' ],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )

		stdout, stderr = process.communicate()
		# Error in running command 
		if process.returncode != 0:
			response["response"] = stderr
			return ( False, response )

		zpool_list = stdout.splitlines()
		# No zpool
		if len( zpool_list ) == 0:
			response["response"] = "No zpool availiabl.e"
			return ( False, response )
		# Title line expected
		if zpool_list[0].split() != title_line:
			response["response"] = "Invalid zpool list format."
			return ( False, response )
		# Get out title line
		zpool_list.pop(0)

		pools = []
		for line in zpool_list:
		
			tokens = line.split()
			if len( tokens ) != len( title_line ):
				response["response"] = "Invalid zpool list format."
				return ( False, response )
			# First collmun is name of zpool
			name = tokens[0]
			if self.SAFE_MODE and self.expr.match( name ):
				continue

			pools.append( tokens[0] )

		response.update( { "data": pools } )
					
		return ( True, response )

	#-------------------------------------------------------------------------#
	# Get all zpools on the system and return array of zpools properties
	def get_zpool_all( self ):
		# Setting up default response
		response = {}
		response["response"] = "Default response"
		# Get names of all pools on system
		status, api_response = self.list_zpool_names()
				
		if not status:
			response["response"] = "Cannot get list of availiable zpools."
			return ( False, response )

		pool_list = api_response[ "data" ]		
		pools = []

		for pool in pool_list:
			try:
				# Instantiate Pool class for gathering data about zpool
				pools.append( Pool( pool ).get_properties() )

			except ValueError as err:
				# Error during zpool parsing
				response["response"] = ( "Error occure during parsing zpool %s" % ( pool ))
				return ( False, response )


		response.update( { "data": pools } )
		return ( True, response )
	#-------------------------------------------------------------------------#
	# Get properties of zpool.
	def get_zpool( self, name ):
		# Setting up default response
		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( name ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		try:
			# Instantiate Zpool class for gathering data about zpool
			properties = Pool( name ).get_properties()

		except ValueError as err:
			# Error during zpool parsing
			response["response"] = ( "Error occure during parsing zpool %s. Probably does not exist." % ( name ))
			return ( False, response )

		response.update( { "data": properties } )
		return ( True, response )
	#-------------------------------------------------------------------------#
	# Destroy zpool 
	def destroy_zpool( self, name ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( name ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )
		
		# If client want to destroy zpool beside rpool (system pool)		
		if name == "rpool":
			response["response"] = "Cannot destroy rpool, system pool" 
			return ( False, response )	
	
		process = subprocess.Popen( [ '/usr/sbin/zpool', 'destroy', name ],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE
				 )

		stdout, stderr = process.communicate()
		# Process did not end properly => not zero return code
		if process.returncode != 0:
			data["response"] = stderr
			return ( False, response )	

		response["response"] = ( "You have succesfully destroyed pool %s" % ( name ))

		return ( True, response )
	#-------------------------------------------------------------------------#
	# List sources that can be used for zpool create
	def list_sources( self ):

		response = {}
		response["response"] = "Default response"
		# Call bash script to handle list sources
		process = subprocess.Popen( [ '/usr/wzfsadm/app/model/modules/PoolModule/shell/listsources.sh', self.FILE_SOURCES ],
						stdout=subprocess.PIPE,
						stderr=subprocess.PIPE
					 )

		stdout, stderr = process.communicate()
		# Process ended badly
		if process.returncode != 0:
			response["response"] = stderr
			return ( False, response )	
		
		# Initialize array with sources
		# Get ROOT pool devices
		rpool_devices = []
		try:
			# Instantiate Zpool class for gathering data about zpool
			rpool = Pool( 'rpool' ).get_properties()

		except ValueError as err:
			# Error during zpool parsing
			response["response"] = ( "Cannot parse rpool to compare available devices.")
			return ( False, response )

		rpool_config = rpool["config"]
		config = rpool_config[0]["config"]
		for device in config:
			if device["config"]:
				# Device is not disk or file
				for list_node in device["config"]:
					rpool_devices.append( list_node["name"] )
			else:
				rpool_devices.append( device["name"] )		
		
		sources = []

		lines = stdout.splitlines()
		for line in lines:
			# Line structure NAME TYPE STATUS
			try:
				name, source_type, status = line.split()
			except ValueError as err:
				print err
				continue

			source = dict()

			flag = False

			for rpool_dev in rpool_devices:
				# If disk or partition is part of rpool dont show
				# c0t1d0.. we take name to d[1-9]etc.
				index_d = rpool_dev.index( 'd' ) + 2
				expr = re.compile( rpool_dev[:index_d] )
				if expr.match( name ):
					flag = True
					break
				
			source.update( { "name":name,
					 "type":source_type,
					 "status":status 	 } )
			# Only if disk is not part of rpool
			if not flag: sources.append( source )

		response.update( { "data": sources } )
		return ( True, response )	

	#-------------------------------------------------------------------------#
	# Create Zpool
	# Name is name of pool that we want to create
	# Resources is array of resources that zpool will be created from
	def create_zpool( self, name, devices, device_type = None, forced = False ):

		response = {}
		response["response"] = "Default response"

		# If not name
		if not name:
			response["response"] = "Empty name. Cannot create pool with empty name."
			return ( False, response )
		
		# Iterate over file
		if not devices:
			response["response"] = "Empty devices. Cannot create pool from empty devices."
			return ( False, response )
		# We need to create parameters for zpool create
		arguments = devices
		# Combine to create zpool command
		if device_type in [ "mirror", "raidz", "raidz1", "raidz2", "raidz3", "none" ]:
			# Device type is not none
			if device_type != "none":
				arguments.insert( 0, device_type )
		else:
			# Not valid device type
			response["response"] = "Not valid device type."
			return ( False, response )
		# Inserting name to command
		arguments.insert( 0, name )		
		# If command should be forced
		if forced:
			arguments.insert( 0, "-f" )
		# Basic command structure
		arguments.insert( 0, "create" )
		arguments.insert( 0, "/usr/sbin/zpool" )


		process = subprocess.Popen( arguments,
					    stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE
					  )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Some error during creating zpool
			response["response"] = stderr
			return ( False, response )

		response["response"] = ( "You have succesfuly created zpool %s. Command %s was succesful" % ( name, " ".join( arguments )) ) 
		return ( True, response )	
	#-------------------------------------------------------------------------#
	def property_set( self, target_pool, name, value ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( target_pool ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not target_pool or not name or not value:
			response["response"] = ( "Not enough arguments. Cannot change property %s to value %s." % ( name, value ))
			return ( False, response )

		process = subprocess.Popen( [ "/usr/sbin/zpool", "set", ( "%s=%s" %( name, value )), target_pool ],
					    stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE
					  )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Some error during adding device to zpool
			response["response"] = stderr
			return ( False, response )

		response["response"] = ( "You have succesfuly changed value of %s to %s in zpool %s." % ( name, value, target_pool) ) 

		return ( True, response )
	#-------------------------------------------------------------------------#
	def history( self, pool = "" ):
		response = {}
		response["response"] = "Default response"			
		args = [ "/usr/sbin/zpool", "history" ]
		if pool : args.append( pool )

		process = subprocess.Popen( args,
					    stdout=subprocess.PIPE,
					    stderr=subprocess.PIPE
					  )

		stdout, stderr = process.communicate()

		if process.returncode != 0:
			# Some error during adding device to zpool
			response["response"] = stderr
			return ( False, response )

		response["response"] = ( "History of zpool was successful." ) 
		response["data"] = stdout

		return ( True, response )
	#-------------------------------------------------------------------------#
