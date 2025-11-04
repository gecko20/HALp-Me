import unittest
from functions.get_files_info import *
from functions.get_file_content import *
from functions.write_file import *
from functions.run_python_file import *

# TODO: Use actual assertions
# TODO: Write tests for every function the LLM might call
class TestGetFilesInfo(unittest.TestCase):
    def setUp(self):
        self.working_dir = "calculator"

    def test_current_dir(self):
        result = get_files_info(self.working_dir, directory=".")
        #self.assertEqual(result, 8)
        print("Result for current directory:")
        print(result)

    def test_pkg_dir(self):
        result = get_files_info(self.working_dir, directory="pkg")
        #self.assertEqual(result, 6)
        print("Result for 'pkg' directory:")
        print(result)

    def test_bin_dir(self):
        result = get_files_info(self.working_dir, directory="/bin")
        #self.assertEqual(result, 12)
        print("Result for '/bin' directory:")
        print(result)

    def test_parent_dir(self):
        result = get_files_info(self.working_dir, directory="../")
        #self.assert...
        print("Result for '../' directory:")
        print(result)

class TestGetFileContent(unittest.TestCase):
    def setUp(self):
        self.working_dir = "calculator"

    def test_lorem(self):
        result = get_file_content(self.working_dir, "lorem3.txt")
        truncate_appendage = f'[...File "lorem3.txt" truncated at {MAX_CHARS} characters]'
        self.assertEqual(len(result + truncate_appendage), MAX_CHARS + len(truncate_appendage))

    def test_main_py(self):
        result = get_file_content(self.working_dir, "main.py")
        print("Result for 'main.py':")
        print(result)

    def test_pkg_calculator_py(self):
        result = get_file_content(self.working_dir, "pkg/calculator.py")
        print("Result for 'pkg/calculator.py':")
        print(result)

    def test_bin_cat(self):
        result = get_file_content(self.working_dir, "/bin/cat")
        print("Result for '/bin/cat':")
        print(result)

    def test_pkg_does_not_exist(self):
        result = get_file_content(self.working_dir, "pkg/does_not_exist.py")
        print("Result for 'pkg/does_not_exist.py':")
        print(result)

class TestWriteFile(unittest.TestCase):
    def setUp(self):
        self.working_dir = "calculator"

    def test_lorem(self):
        result = write_file(self.working_dir, "lorem2.txt", "wait, this isn't lorem ipsum")
        print("Result for 'lorem2.txt':")
        print(result)

    def test_more_lorem(self):
        result = write_file(self.working_dir, "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
        print("Result for 'pkg/morelorem.txt':")
        print(result)

    def test_tmp_temp(self):
        result = write_file(self.working_dir, "/tmp/temp.txt", "this should not be allowed")
        print("Result for '/tmp/temp.txt':")
        print(result)

class TestRunPythonFile(unittest.TestCase):
    def setUp(self):
        self.working_dir = "calculator"

    def test_calculator_noargs(self):
        result = run_python_file(self.working_dir, "main.py")
        print("Result for 'main.py'")
        print(result)

    def test_calculator_args(self):
        result = run_python_file(self.working_dir, "main.py", args=["3 + 5"])
        print("Result for 'main.py '3 + 5''")
        print(result)

    def test_calculator_tests(self):
        result = run_python_file(self.working_dir, "tests.py")
        print("Result for 'tests.py'")
        print(result)

    def test_outside_working_dir(self):
        # Should return an error
        result = run_python_file(self.working_dir, "../main.py")
        print("Result for '../main.py'")
        print(result)

    def test_nonexistent_file(self):
        # Should return an error
        result = run_python_file(self.working_dir, "nonexistent.py")
        print("Result for 'nonexistent.py'")
        print(result)

    def test_nonpython_file(self):
        result = run_python_file(self.working_dir, "lorem3.txt")
        print("Result for 'lorem3.txt'")
        print(result)

if __name__ == "__main__":
    unittest.main()