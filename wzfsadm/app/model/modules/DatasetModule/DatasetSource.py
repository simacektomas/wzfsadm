from app.model.modules.BaseModuleClass import BaseModuleClass

import Dataset 
reload( Dataset )
from Dataset import Dataset
import subprocess
import json
import re

class DatasetClass( BaseModuleClass ):
	#-------------------------------------------------------------------------#
	MODULE_NAME = "Dataset Module"
	#-------------------------------------------------------------------------#
	def __init__( self ):
		# Call parent constructor
		BaseModuleClass.__init__( self, self.MODULE_NAME )	
	#-------------------------------------------------------------------------#
	def get_dataset_all( self ):

		response = {}
		response["response"] = "Default response"

		process = subprocess.Popen( [ 'zfs', 'list' ],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
				# Non zero return code
				response["response"] = "Cannot list datasets."
				return ( False, response )

		lines = stdout.splitlines()		
		if not lines[0].split() == [ "NAME", "USED", "AVAIL", "REFER", "MOUNTPOINT" ]:
			response["response"] = "Invalid format of zfs list output."
			return ( False, response )
		# Get rid of label line
		lines.pop(0)
		datasets = []

		for line in lines:
			try:
				dataset = {}
				tokens = line.split()
				dataset["name"] = tokens[0]
				dataset["used"] = tokens[1]
				dataset["avail"] = tokens[2]
				dataset["refer"] = tokens[3]
				dataset["mountpoint"] = tokens[4]
				if self.SAFE_MODE and self.expr.match( dataset["name"] ):
					continue
				datasets.append( dataset )
			except Exception as err:
				# Cannot parse or create Dataset
				print err
				continue

		response["status"] = "OK"
		response["response"] = "Dataset are in data key."
		response["data"] = datasets

		return ( True, response )
	#-------------------------------------------------------------------------#
	def get_dataset( self, name ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( name ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		try:
			instance = Dataset( name )
		except ValueError:
			response["response"] = "Cannot create instance of dataset ( Does not exist etc.)."
			return ( False, response )

		response["status"] = "OK"
		response["response"] = "Instance of Dataset are in data key."
		response["data"] = instance

		return ( True, response )
	#-------------------------------------------------------------------------#
	def create_dataset( self, dataset, create_parents = False ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( dataset ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not dataset:
			response["response"] = "Cannot create dataset without dataset name."
			return ( False, response )
				
		arguments = []
		arguments.insert( 0, dataset )
		if create_parents:
			# Create all parents
			arguments.insert( 0, '-p' )
		arguments.insert( 0, 'create' )
		arguments.insert( 0, '/usr/sbin/zfs' )

		process = subprocess.Popen( arguments ,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			# Some error during creating dataset
			response["response"] = stderr
			return ( False, response )
		
		response["status"] = "OK"
		response["response"] = ( "You have successfully created dataset %s." % ( dataset ) )

		return ( True, response )
	#-------------------------------------------------------------------------#
	def destroy_dataset( self, dataset, destroy_children = False, forced = False  ):
		
		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( dataset ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not dataset:
			response["response"] = "Cannot destroy dataset without dataset name."
			return ( False, response )

		arguments = []
		arguments.insert( 0, dataset )

		if destroy_children:
			# Destroy all children
			arguments.insert( 0, '-r' )

		if forced:
			# Create all parents
			arguments.insert( 0, '-f' )
		# Basisc command
		arguments.insert( 0, 'destroy' )
		arguments.insert( 0, '/usr/sbin/zfs' )

		process = subprocess.Popen( arguments,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			# Some error during creating dataset
			response["response"] = stderr
			return ( False, response )
		
		response["status"] = "OK"
		response["response"] = ( "You have successfully destroy dataset %s. Command %s was executed." % ( dataset, " ".join( arguments ) ) )

		return ( True, response )
	#-------------------------------------------------------------------------#
	def create_snapshot( self, dataset, snapshot, descendant = False ):
		
		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( dataset ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not dataset or not snapshot:
			response["response"] = ( "Invalid dataset name %s or snapshot name %s." % ( dataset, snapshot ) )
			return ( False, response )

		arguments = []
		arguments.insert( 0, ( "%s@%s" % ( dataset, snapshot ) ) )
		# Should snapshot be created for all descendant datasets
		if descendant:
			arguments.insert( 0, "-r" )
		# Basic command
		arguments.insert( 0, "snapshot" )
		arguments.insert( 0, "/usr/sbin/zfs" )

		process = subprocess.Popen( arguments,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			# Some error during creating dataset
			response["response"] = stderr
			return ( False, response )

		response["status"] = "OK"
		response["response"] = ( "You have successfully created snapshot %s of %s dataset. Command %s was executed." % ( snapshot, dataset, " ".join( arguments ) ) )
		return ( True, response )
	#-------------------------------------------------------------------------#
	def mount_dataset( self, dataset, options ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( dataset ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not dataset:
			response["response"] = "Empty dataset name. Cannot mount dataset without name."
			return ( False, response )

		arguments = []
		arguments.insert( 0, dataset )
		# If some temporary options set them
		if options:
			arguments.insert( 0, ','.join( options ) )
			arguments.insert( 0, '-o' )

		arguments.insert( 0, "mount" )
		arguments.insert( 0, "/usr/sbin/zfs" )

		process = subprocess.Popen( arguments,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			# Some error during creating dataset
			response["response"] = stderr
			return ( False, response )

		response["status"] = "OK"
		response["response"] = ( "You have mounted %s dataset. Command %s was executed." % ( dataset, " ".join( arguments ) ) )
		return ( True, response )
	#-------------------------------------------------------------------------#
	def unmount_dataset( self, dataset, forced = False ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( dataset ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not dataset:
			response["response"] = "Empty dataset name. Cannot unmount dataset without name."
			return ( False, response )

		arguments = []
		arguments.insert( 0, dataset )
		# Check if command should be forced executed
		if forced:
			arguments.insert( 0, "-f" )
		# Basic commnad
		arguments.insert( 0, "unmount" )
		arguments.insert( 0, "/usr/sbin/zfs" )
		# Run command
		process = subprocess.Popen( arguments,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			# Some error during creating dataset
			response["response"] = stderr
			return ( False, response )

		response["status"] = "OK"
		response["response"] = ( "You have unmounted %s dataset. Command %s was executed." % ( dataset, " ".join( arguments ) ) )
		return ( True, response )
	#-------------------------------------------------------------------------#
	def rollback_dataset( self, snapshot, destroy_more_recent = False ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( dataset ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not snapshot:
			response["response"] = "Empty snapshot name. Cannot rollback dataset without snapshot name."
			return ( False, response )

		arguments = []
		arguments.insert( 0, snapshot )
		# Check if command should destroy more recent snapshots
		if destroy_more_recent:
			arguments.insert( 0, '-r' )
		# Basic command
		arguments.insert( 0, "rollback" )
		arguments.insert( 0, "/usr/sbin/zfs" )
		# Run command
		process = subprocess.Popen( arguments,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			# Some error during creating dataset
			response["response"] = stderr
			return ( False, response )

		response["status"] = "OK"
		response["response"] = ( "You successfuly rollback dataset to snapshot %s. Command %s was executed." % ( snapshot, " ".join( arguments ) ) )
		return ( True, response )
	#-------------------------------------------------------------------------#
	def property_set( self, dataset, property_name, property_value, recursively = False ):

		response = {}
		response["response"] = "Default response"

		if self.SAFE_MODE and self.expr.match( dataset ):
			response["response"] = "Application is running in safe mode. Cannot process operation over system pool rpool."
			return ( False, response )

		if not dataset or not property_name or not property_value:
			response["response"] = "Not enough parameters to complete action."
			return ( False, response )

		arguments = []
		arguments.insert( 0, dataset )
		arguments.insert( 0, ( "%s=%s" %( property_name, property_value ) ) )
		# Check if property should be set recursively
		if recursively:
			arguments.insert( 0, '-r' )
		# Basic command
		arguments.insert( 0, "set" )
		arguments.insert( 0, "/usr/sbin/zfs" )

		process = subprocess.Popen( arguments,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			 )
		
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			# Some error during creating dataset
			response["response"] = stderr
			return ( False, response )

		response["status"] = "OK"
		response["response"] = ( "You successfuly set %s property to %s.Command %s was executed." % ( property_name, property_value, " ".join( arguments ) ) )
		return ( True, response )
	#-------------------------------------------------------------------------#
	def user_quota( self, dataset, username, quota, recursively = False ):

		response = {}
		response["response"] = "Default response"
		
		property_name = "userquota@%s" % ( username )

		return self.property_set( dataset, property_name, quota, recursively )
	#-------------------------------------------------------------------------#
	def group_quota( self, dataset, group, quota, recursively = False ):
		
		response = {}
		response["response"] = "Default response"
		
		property_name = "groupquota@%s" % ( group )

		return self.property_set( dataset, property_name, quota, recursively )
	#-------------------------------------------------------------------------#
