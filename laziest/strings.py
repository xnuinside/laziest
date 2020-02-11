# main
file_output = "import pytest\n"
test_method_prefix = 'test_'
func_full_prefix = f'def {test_method_prefix}'
# tests strings
SP_4 = "    "
pytest_async_decorator = "@pytest.mark.asyncio\n"
pytest_parametrize_decorator = "@pytest.mark.parametrize('params', [])\n"
method_signature = func_full_prefix + "{method}():\n{SP_4}"
async_method_signature = pytest_async_decorator + 'async ' + method_signature
base_object_method_signature = func_full_prefix + "test_{method}({self}):\n{SP_4}{SP_4}\n"
class_method_signature = "\n{SP_4}" + base_object_method_signature
class_async_method_signature = "\n{SP_4}" + pytest_async_decorator + base_object_method_signature
class_signature = "class Test{cls_name}:{SP_4}\n"
log_capsys_str = 'captured = capsys.readouterr()'

assert_string = "assert"

async_io_aware_text = "# Need to install pytest-asyncio package " \
                      "to get possible run tests for async method\n\n"
