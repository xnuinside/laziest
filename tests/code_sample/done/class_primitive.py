import uuid


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
	def static_method_two():
		dict_var = {'num': 'alias', 'value_two': 1}
		second_dir = {'str': '_123'}
		alias_var = dict_var
		result = (dict_var['num'] * alias_var['value_two']) + second_dir['str']
		return result, second_dir, alias_var

	def object_method_with_return_uuid(self):
		return {'id': uuid.uuid4().hex, 'days': 0}
