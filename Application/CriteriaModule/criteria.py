



#!/usr/bin/env python3
from SettingsModule.settings import question_collection_name, default_document_limit,\
									indian_time, permissions, category_collection_name,\
									app_super_admin, app_super_admin_pwd, app_super_admin_user_id,\
									user_collection_name, criteria_collection_name, \
									indian_time, sub_criteria_collection_name

from GenericModule.generic import GenericPermissions, Generic, Generics

from AuthenticationModule.authentication import auth
from tornado.web import asynchronous
from tornado.gen import coroutine
import tornado
from LoggingModule.logging import logger
import hashlib
import json
import traceback
import time




class CriteriaPermissions(GenericPermissions):
	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]
		self.module_collection = self.db[criteria_collection_name]
		self.child_collection = self.db[sub_criteria_collection_name]
		self.child_collection_name = sub_criteria_collection_name
		self.document_id = "criteria_id"
		self.document_name = "criteria"


@auth
class Criteria(Generic):
	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]
		self.module_collection = self.db[criteria_collection_name]
		self.child_collection = self.db[sub_criteria_collection_name]
		self.child_collection_name = sub_criteria_collection_name
		self.document_id = "criteria_id"
		self.document_name = "criteria"



class Criterion(Generics):
	"""
	Return questions 
	Questions can filtered according to the 
		admin created id
		superadmin id
		category id
		date created	
	"""

	def initialize(self):
		self.db = self.settings["db"]
		self.user_collection = self.db[user_collection_name]
		self.module_collection = self.db[criteria_collection_name]
		self.child_collection = self.db[sub_criteria_collection_name]
		self.child_collection_name = sub_criteria_collection_name
		self.document_id = "criteria_id"
		self.document_name = "sub_category"
















