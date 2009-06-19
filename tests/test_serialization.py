#!/usr/bin/python
# -*- coding: utf-8 -*-

import cPickle
import sys
import os
import unittest
import uuid
sys.path.insert(0, os.pardir)
sys.path.append(os.getcwd())

from carrot.serialization import registry

# For content_encoding tests
unicode_string = u'abcdé\u8463'
unicode_string_as_utf8 = unicode_string.encode('utf-8')
latin_string = u'abcdé'
latin_string_as_latin1 = latin_string.encode('latin-1')
latin_string_as_utf8 = latin_string.encode('utf-8')


# For serialization tests
py_data = {"string": "The quick brown fox jumps over the lazy dog",
        "int": 10,
        "float": 3.14159265,
        "unicode": u"Thé quick brown fox jumps over thé lazy dog",
        "list": ["george", "jerry", "elaine", "cosmo"],
}

# JSON serialization tests
json_data = ('{"int": 10, "float": 3.1415926500000002, '
             '"list": ["george", "jerry", "elaine", "cosmo"], '
             '"string": "The quick brown fox jumps over the lazy '
             'dog", "unicode": "Th\\u00e9 quick brown fox jumps over '
             'th\\u00e9 lazy dog"}')

# Pickle serialization tests
pickle_data = cPickle.dumps(py_data)

# YAML serialization tests
yaml_data = ('float: 3.1415926500000002\nint: 10\n'
             'list: [george, jerry, elaine, cosmo]\n'
             'string: The quick brown fox jumps over the lazy dog\n'
             'unicode: "Th\\xE9 quick brown fox '
             'jumps over th\\xE9 lazy dog"\n')

# Hessian serialization tests
hessian_data =  ('r\x01\x00fB\x00\x03intI\x00\x00\x00\nB\x00\x05float'
                 'D@\t!\xfbS\xc8\xd4\xf1B\x00\x04listVl\x00\x00\x00\x04'
                 'B\x00\x06georgeB\x00\x05jerryB\x00\x06elaineB\x00\x05'
                 'cosmozB\x00\x06stringB\x00+The quick brown fox jumps '
                 'over the lazy dogB\x00\x07unicodeS\x00+Th\xc3\xa9 quick '
                 'brown fox jumps over th\xc3\xa9 lazy dogzz')


class TestSerialization(unittest.TestCase):

    def test_content_type_decoding(self):
        content_type = 'plain/text'

        self.assertEquals(unicode_string,
                          registry.decode(
                              unicode_string_as_utf8, 
                              content_type='plain/text', 
                              content_encoding='utf-8'))
        self.assertEquals(latin_string,
                          registry.decode(
                              latin_string_as_latin1, 
                              content_type='application/data', 
                              content_encoding='latin-1'))

    def test_content_type_binary(self):
        content_type = 'plain/text'

        self.assertNotEquals(unicode_string,
                             registry.decode(
                                 unicode_string_as_utf8, 
                                 content_type='application/data', 
                                 content_encoding='binary'))

        self.assertEquals(unicode_string_as_utf8,
                          registry.decode(
                              unicode_string_as_utf8, 
                              content_type='application/data', 
                              content_encoding='binary'))

    def test_content_type_encoding(self):
        self.assertEquals(unicode_string_as_utf8,
                          registry.encode(
                              unicode_string, serializer="raw")[-1])
        self.assertEquals(latin_string_as_utf8, 
                          registry.encode(
                              latin_string, serializer="raw")[-1])

    def test_json_decode(self):
        self.assertEquals(py_data,
                          registry.decode(
                              json_data, 
                              content_type='application/json', 
                              content_encoding='utf-8'))
        
    def test_json_encode(self):
        self.assertEquals(registry.decode(
                              registry.encode(py_data, serializer="json")[-1], 
                              content_type='application/json', 
                              content_encoding='utf-8'),
                          registry.decode(
                              json_data, 
                              content_type='application/json', 
                              content_encoding='utf-8'))

    def test_yaml_decode(self):
        self.assertEquals(py_data,
                          registry.decode(
                              yaml_data, 
                              content_type='application/x-yaml', 
                              content_encoding='utf-8'))
        
    def test_yaml_encode(self):
        self.assertEquals(registry.decode(
                              registry.encode(py_data, serializer="yaml")[-1], 
                              content_type='application/x-yaml', 
                              content_encoding='utf-8'),
                          registry.decode(
                              yaml_data, 
                              content_type='application/x-yaml', 
                              content_encoding='utf-8'))
    # 
    # def test_hessian_decode(self):
    #     print '---------'
    #     print registry.decode(
    #         hessian_data, 
    #         content_type='application/x-hessian', 
    #         content_encoding='binary')
    #     print '---------'
    #     self.assertEquals(py_data,
    #                       registry.decode(
    #                           hessian_data, 
    #                           content_type='application/x-hessian', 
    #                           content_encoding='binary'))
    #     
    # def test_hessian_encode(self):
    #     self.assertEquals(registry.decode(
    #                           registry.encode(py_data, serializer="hessian")[-1], 
    #                           content_type='application/x-hessian', 
    #                           content_encoding='binary'),
    #                       registry.decode(
    #                           hessian_data, 
    #                           content_type='application/x-hessian', 
    #                           content_encoding='binary'))

    def test_pickle_decode(self):
        self.assertEquals(py_data,
                          registry.decode(
                              pickle_data, 
                              content_type='application/x-python-serialize', 
                              content_encoding='binary'))
        
    def test_pickle_encode(self):
        self.assertEquals(pickle_data,
                          registry.encode(py_data, 
                              serializer="pickle")[-1])


if __name__ == '__main__':
    unittest.main()