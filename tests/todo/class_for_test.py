class ClassForTest(object):

	def __init__(self):
		pass

	def object_method_1(self):
		pass

	def object_method_2(self):
		pass

	@classmethod
	def class_method_one(cls):
		pass

	@classmethod
	def class_method_two(cls):
		pass

	@staticmethod
	def static_method_one():
		result = 5 + 9
		alias = result
		return result * alias

	@staticmethod
	def static_method_two(self):
		pass


class ClassForTestWithInit(object):

	def __init__(self, name):
		pass

	def object_method_1(self):
		pass

	def object_method_2(self):
		pass

	@classmethod
	def class_method_one(cls):
		pass
