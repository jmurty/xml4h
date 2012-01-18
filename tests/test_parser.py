import unittest
import os

from xml4h import parser, nodes

class BaseParserTest(object):

    def test_parse_file(self):
        xml_file_path = os.path.join(
            os.path.dirname(__file__), 'example_doc.small.xml')
        wrapped_doc = self.parse_file(xml_file_path)
        self.assertIsInstance(wrapped_doc, nodes.Document)
        self.assertEqual(8, len(wrapped_doc.find()))
        # Check element namespaces
        self.assertEqual(
            ['DocRoot', 'NSDefaultImplicit', 'NSDefaultExplicit', 'Attrs1', 'Attrs2'],
            [n.name for n in wrapped_doc.find(ns_uri='urn:default')])
        self.assertEqual(
            ['NSCustomExplicit', 'myns:NSCustomWithPrefixImplicit', 'myns:NSCustomWithPrefixExplicit'],
            [n.name for n in wrapped_doc.find(ns_uri='urn:custom')])
        self.assertEqual(
            ['NSCustomExplicit', 'NSCustomWithPrefixImplicit', 'NSCustomWithPrefixExplicit'],
            [n.local_name for n in wrapped_doc.find(ns_uri='urn:custom')])
        # Check attribute namespaces
        self.assertEqual([nodes.Node.XMLNS_URI, nodes.Node.XMLNS_URI],
            [n.namespace_uri for n in wrapped_doc.root.attribute_nodes])
        attrs1_elem = wrapped_doc.find_first('Attrs1')
        self.assertEqual([None, None],
            [n.namespace_uri for n in attrs1_elem.attribute_nodes])
        attrs2_elem = wrapped_doc.find_first('Attrs2')
        self.assertEqual(['urn:custom', 'urn:custom'],
            [n.namespace_uri for n in attrs2_elem.attribute_nodes])


class TestXmlDomParser(unittest.TestCase, BaseParserTest):

    def parse_string(self, xml_str):
        return parser.parse_string_xmldom(xml_str)

    def parse_file(self, xml_file):
        return parser.parse_file_xmldom(xml_file)
