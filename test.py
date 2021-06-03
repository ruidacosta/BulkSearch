import unittest
import os
import os.path
import shutil

import BulkSearch


class TestStringMethods(unittest.TestCase):
    """
    Test files
    """

    def test_get_all_files_no_subdir(self):
        folder = prepare_folder_files(False, True, False)
        result = BulkSearch.get_all_files(folder)
        remove_all(folder)
        expect = ['file_1', 'file_2', 'file_3']
        self.assertEqual(result, expect)

    def test_get_all_files_with_subdir(self):
        folder = prepare_folder_files(True, True, True)
        result = BulkSearch.get_all_files(folder)
        remove_all(folder)
        expect = ['file_1', 'file_2', 'file_3', 'file_a', 'file_b', 'file_c', 'file_a', 'file_b', 'file_c', 'file_a',
                  'file_b', 'file_c']
        self.assertEqual(result, expect)

    def test_get_all_files_empty(self):
        folder = prepare_folder_files()
        result = BulkSearch.get_all_files(folder)
        remove_all(folder)
        self.assertEqual(result, [])

    def test_get_all_files_not_exists(self):
        folder = 'Something'
        result = BulkSearch.get_all_files(folder)
        self.assertEqual(result, [])

    '''
    Test search 
    '''

    def test_search_on_file_single_result(self):
        abs_file = create_test_file('something.txt')
        result = BulkSearch.search_on_file(abs_file, 'patato')
        remove_all(abs_file)
        self.assertTrue(len(result) == 1)

    def test_search_on_file_multiple_result(self):
        abs_file = create_test_file('something.txt')
        result = BulkSearch.search_on_file(abs_file, 'bla')
        remove_all(abs_file)
        self.assertTrue(len(result) == 4)

    def test_search_on_file_no_result(self):
        abs_file = create_test_file('something.txt')
        result = BulkSearch.search_on_file(abs_file, 'something')
        remove_all(abs_file)
        self.assertEqual(result, [])

    def test_search_on_file_single_result_regex(self):
        abs_file = create_test_file('something.txt')
        result = BulkSearch.search_on_file(abs_file, '\d+')
        remove_all(abs_file)
        self.assertTrue(len(result) == 1)

    def test_search_on_file_multiple_result_regex(self):
        abs_file = create_test_file('something.txt')
        result = BulkSearch.search_on_file(abs_file, '<.*?>')
        remove_all(abs_file)
        self.assertTrue(len(result) == 2)

    def test_search_on_file_no_result_regex(self):
        abs_file = create_test_file('something.txt')
        result = BulkSearch.search_on_file(abs_file, '[1-5]+')
        remove_all(abs_file)
        self.assertEqual(result, [])

    '''
    Test output
    '''

    def test_output_to_txt(self):
        data = {'test.py': [(2, 'Lorem ipsum dolor sit amet'), (6, 'estibulum ipsum nibh')],
                'amother.log': [(4, 'Vivamus sem nisl'), (9, 'Suspendisse iaculis lobortis diam a porttitor')]}
        expect = '''test.py
Line 2: Lorem ipsum dolor sit amet
Line 6: estibulum ipsum nibh

amother.log
Line 4: Vivamus sem nisl
Line 9: Suspendisse iaculis lobortis diam a porttitor

'''
        msg = BulkSearch.output_to_txt(data)
        self.assertEqual(msg, expect)

    def test_output_to_txt_empty(self):
        msg = BulkSearch.output_to_txt({})
        self.assertEqual(msg, '')

    def test_output_to_xml(self):
        data = {'test.py': [(2, 'Lorem ipsum dolor sit amet'), (6, 'estibulum ipsum nibh')],
                'amother.log': [(4, 'Vivamus sem nisl'), (9, 'Suspendisse iaculis lobortis diam a porttitor')]}
        expect = '<search><string>string</string><files><file><name>test.py</name></file><matchs><match><line_number>2</line_number><line_string>Lorem ipsum dolor sit amet</line_string></match><match><line_number>6</line_number><line_string>estibulum ipsum nibh</line_string></match></matchs><file><name>amother.log</name></file><matchs><match><line_number>4</line_number><line_string>Vivamus sem nisl</line_string></match><match><line_number>9</line_number><line_string>Suspendisse iaculis lobortis diam a porttitor</line_string></match></matchs></files></search>'
        msg = BulkSearch.output_to_xml(data, 'string')
        self.assertEqual(msg, expect)

    def test_output_to_xml_empty(self):
        expect = '<search><string>string</string><files /></search>'
        msg = BulkSearch.output_to_xml({}, 'string')
        self.assertEqual(msg, expect)

    def test_output_to_json(self):
        data = {'test.py': [(2, 'Lorem ipsum dolor sit amet'), (6, 'estibulum ipsum nibh')],
                'amother.log': [(4, 'Vivamus sem nisl'), (9, 'Suspendisse iaculis lobortis diam a porttitor')]}
        expect = '{"string": "string", "data": {"test.py": [[2, "Lorem ipsum dolor sit amet"], [6, "estibulum ipsum nibh"]], "amother.log": [[4, "Vivamus sem nisl"], [9, "Suspendisse iaculis lobortis diam a porttitor"]]}}'
        msg = BulkSearch.output_to_json(data, 'string')
        self.assertEqual(msg, expect)

    def test_output_to_json_empty(self):
        expect = '{"string": "string", "data": {}}'
        msg = BulkSearch.output_to_json({}, 'string')
        self.assertEqual(msg, expect)


def prepare_folder_files(subdirs: bool = False, files: bool = False, subdir_file: bool = False) -> str:
    folder = os.path.abspath('test_dir')
    os.mkdir(folder)
    os.chdir(folder)
    if subdirs:
        # Create 3 folders
        for folder_name in ['folder1', 'folder2', 'folder3']:
            os.mkdir(folder_name)
    if files:
        # Create 3 files
        for file_name in ['file_1', 'file_2', 'file_3']:
            with open(file_name, 'w') as fd:
                fd.write('blablabla')
    if subdir_file:
        # Create 3 files inside each existent folder
        folders = os.listdir('.')
        for sub_folder in folders:
            if os.path.isdir(sub_folder):
                os.chdir(sub_folder)
                for file_name in ['file_a', 'file_b', 'file_c']:
                    with open(file_name, 'w') as fd:
                        fd.write('bla bla bla')
                os.chdir('..')
    os.chdir('..')
    return folder


def remove_all(item: str):
    item_abs = os.path.abspath(item)
    if os.path.isfile(item_abs):
        os.remove(item_abs)
    elif os.path.isdir(item_abs):
        abs_folder = os.path.abspath(item)
        shutil.rmtree(abs_folder)


def create_test_file(filename: str) -> str:
    content = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque dapibus tincidunt mauris in dignissim. Integer interdum 
molestie odio, vel interdum bla risus vulputate eu. Vestibulum ipsum nibh, commodo a consequat et, efficitur eget ante. Nam 
commodo enim et patato tellus ullamcorper, eget lobortis ipsum porta. Proin id nisi placerat, aliquet metus et, varius felis. 
Aliquam non purus nec velit tincidunt accumsan. Donec bla quis nibh mauris. Morbi commodo felis non est consequat hendrerit. 
In pellentesque arcu sed leo lobortis tempus. Vivamus sem nisl, congue ac lorem sed, maximus sodales elit. Sed ut orci non 
velit cursus ultricies. Nunc est class purus, bla commodo vitae finibus ac, tempus <htlm> vitae sem.
Phasellus non dapibus orci. Sed dapibus tellus id nunc sollicitudin efficitur. Maecenas pulvinar lobortis sapien nec placerat.
Sed viverra arcu at porta luctus. Vivamus mattis hendrerit lacus, eu bibendum metus faucibus eu. Nullam vitae enim ultricies, 
molestie sapien tempus, 666 sollicitudin ligula. Etiam bibendum ante pulvinar neque mollis porttitor. Suspendisse hendrerit 
eleifend metus. Praesent ornare vel odio eu bla suscipit. Cras tincidunt erat augue, in vulputate ante convallis in. Ut eu 
pulvinar </title> risus, ac bibendum dolor. Suspendisse iaculis lobortis diam a porttitor.
'''
    with open(filename, 'w') as fd:
        fd.write(content)
    return os.path.abspath(filename)


if __name__ == '__main__':
    unittest.main()
