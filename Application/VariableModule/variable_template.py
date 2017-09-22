import tornado.options
import tornado.web
from SettingsModule.settings import user_collection_name, domain_collection_name, template_collection_name,\
					indian_time, variable_collection_name, variable_template_collection_name, variable_template_bucket
from LoggingModule.logging import logger
from tornado.ioloop import IOLoop
import hashlib
import jwt
import json 
from pprint import pprint 
import uuid
import time
import math

#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

from GeneralModule.cors import cors

def make_ngrams(word, min_size=2):
		"""
		basestring       word: word to split into ngrams
		int   min_size: minimum size of ngrams
		"""
		length = len(word)
		size_range = range(min_size, max(length, min_size) + 1)
		return list(set(
			word[i:i + size]
			for size in size_range
			for i in range(0, max(0, length - size) + 1)
			))


class VariableTemplates(tornado.web.RequestHandler):
	#TODO: Need to implement users whoc can make variables
	def initialize(self):
			self.db = self.settings["db"]
			self.variable_collection = self.db[variable_collection_name]
			self.collection = self.db[variable_template_collection_name]
			self.user_collection = self.db[user_collection_name]

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def options(self, domain_id=None, user_id=None):
        # no body
		self.set_status(204)
		self.finish()




	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  get(self):
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		try:
			skip = int(self.request.arguments.get("skip")[0].decode("utf-8"))
			limit = int(self.request.arguments.get("limit")[0].decode("utf-8"))
		except Exception:
			skip = 0
			limit = 15
		
		try:
			variabletemplate_id = self.request.arguments.get("variabletemplate_id")[0].decode("utf-8")
		except Exception:
			variabletemplate_id= None
		try:
			search_text = self.request.arguments.get("search_text")[0].decode("utf-8")
		except Exception:
			search_text = None

		user = yield self.user_collection.find_one({"user_id": user_id})

		if not variabletemplate_id:
			variabletemplates = []
			if search_text:
				variabletemplate_count = yield self.collection.find({ 
							"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False}).count()
				
				pprint ("This is the template count %s"%variabletemplate_count)
				cursor = self.collection.find({
							"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False, "variable_array": False}).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					variabletemplates.append(cursor.next_object())
			
			else:
				variabletemplate_count = yield self.collection.find(projection={"_id": False, "ngrams": False}).count()
				cursor = self.collection.find(projection={"_id": False, "variable_array": False, "ngrams": False}).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					variabletemplates.append(cursor.next_object())

			variabletemplate_ids = []
			for module in variabletemplates:
					variabletemplate_ids.append(module.get("variabletemplate_id"))

			message = {"error": True, "success": False, "message": "Success", "data": {"variabletemplates": variabletemplates, "variabletemplate_ids": variabletemplate_ids, 
						"variabletemplate_count": variabletemplate_count, "pages": math.ceil(variabletemplate_count/limit)}}

		else:
				variabletemplate = yield self.collection.find_one({}, projection={"_id": False, "user_id": False, "ngrams": False, "utc_epoch": False})
				if not variabletemplate:
					raise Exception("No such variable template exists")
				message = {"error": False, "success": True,  "data": variabletemplate}

		self.write(message)
		self.finish()
		return


	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  delete(self):
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		variabletemplate_id = self.request.arguments.get("variabletemplate_id")[0].decode("utf-8")
		try:
			#post_arguments = json.loads(self.request.body.decode("utf-8"))
			#user_id = post_arguments.get("user_id", None) ##who created this category
			if not variabletemplate_id:
				raise Exception("Please send the variable template id")
		
			variable = yield self.collection.find_one({"variabletemplate_id": variabletemplate_id})
			user = yield self.user_collection.find_one({"user_id": user_id})
			if user["user_type"] == "superadmin":
				yield self.collection.delete_one({"variabletemplate_id": variabletemplate_id})
			else:
				raise Exception("You have insufficient permissions to delete this variable template")
		
		except Exception as e:
			print (e)
			self.set_status(403)
			self.write(str(e))
			self.finish()
			return 


		self.write({"data": variable_id})
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  post(self):
		"""

		he variable collection will have all the variables in it, With every variable there will
		be a data_type attached to it. While creating a varaible template, The user either must be 
		a superadmin or must have variable_template True

		A user which creating a Variable Template can select variables from all the templates, and then
		Edit their values,
		This variable template once created can be attached to Main template which will then be served 
		to students.
		"""

		print (self.request.body)
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		print (post_arguments)
		variabletemplate_name = post_arguments.get("variabletemplate_name")
		description = post_arguments.get("description")
		user_id = post_arguments.get("user_id")
		variable_array = post_arguments.get("variable_array")
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			user = yield self.user_collection.find_one({"user_id": user_id})

			if user["user_type"] != "superadmin":
				if not user["variable_template"]:
					raise Exception ("You do not have sufficient permissions to create variable template")

			if not variabletemplate_name:
				raise Exception("Variable Template Name is missing")

			if not identifier.startswith("#"):
				raise Exception("Identifier must starts with #")


			if user["user_type"] == "superadmin":
				creation_approval = True
			else:
				creation_approval = False


			variable_object = yield self.collection.find_one({"variable_name": variable_name}, projection={"_id": False, "variabletemplate_name": True})
			if variable_object:
				raise Exception("variable has already been made, Please select a diffrent name for the variable")

			_id = str(uuid.uuid4())

			variable_object = {"variable_id": _id, "variabletemplate_name": variabletemplate_name,  "utc_epoch": time.time(), "description": description,
									"indian_time": indian_time(), "ngrams": " ".join(make_ngrams(variable_name)),
									"user_id": user_id,  "variable_array": variable_array, "creation_approval": creation_approval, 
									"username": user["username"]
									 }
			yield self.collection.insert_one(variable_object)
		
		except Exception as e:
				logger.error(e)
				self.set_status(401)
				self.write(e.__str__())
				#self.write({"error": False, "success": True})
				self.finish()
				return 

		variable_object.pop("_id")
		message = {"error": False, "success": True, "data": {"variabletemplate": variable_object, "variabletemplate_id": _id}}
		pprint (message)
		self.write(message)
		self.finish()
		return 


	@cors
	@staticmethod
	@tornado.gen.coroutine
	def upload_image(self):
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		variable_template_name = self.request.arguments.get("variable_template_name")[0].decode("utf-8")
		variable_name = self.request.arguments.get("variable_name")[0].decode("utf-8")
		
		user = yield self.users.find_one({"user_id": user_id}, projection={"_id": False, "ngrams": False})
		parent = yield self.parent_collection.find_one({"module_id": parent_id}, projection={"_id": False, "ngrams": False})


		if not user or not parent:
			raise Exception("user_id and parent_id must be provided")
			
		arg = self.request.files["image_data"][0]


		images = self.request.files["image_data"]
		
		s3_urls = []
		for image in images:
			image_data = image.get("body")
			image_name = image.get("filename")
			image_content_type = image.get("content_type")



		def push_to_s3(image_data):
			bytesIO = BytesIO()
			bytesIO.write(image_data)
			bytesIO.seek(0)
        
			__name = "%s/%s/%s"%(parent["module_name"], user["username"], image_name)
			name = __name.lower().replace(" ", "").replace("nanoskill-", "")

			s3connection.put_object(Body=bytesIO, Bucket=bucket_name, Key=name, 
								ContentType=image_content_type, Metadata= {"user_id": user_id, 
								"variable_name": variable_name,
								 "variable_template_name": variable_template_name})

			url = s3connection.generate_presigned_url('get_object', 
									Params = {'Bucket': bucket_name, 'Key': name}, ExpiresIn = 10)
			return url
		
		##TODO: https://gist.github.com/kn9ts/4b5a9942b6afbfc2534f2f14c87b9b54
		##TODO: https://github.com/jmenga/requests-aws-sign
		self.write({"link": url})
		self.finish()
		return


