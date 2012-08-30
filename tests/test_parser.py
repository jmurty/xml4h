# -*- coding: utf-8 name> -*-
import unittest
import os
import re

from xml4h import parser, nodes

class BaseParserTest(object):

    @property
    def small_xml_file_path(self):
        return os.path.join(os.path.dirname(__file__), 'example_doc.small.xml')

    @property
    def unicode_xml_file_path(self):
        return os.path.join(os.path.dirname(__file__), 'example_doc.unicode.xml')

    def test_parse_file(self):
        wrapped_doc = self.parse_file(self.small_xml_file_path)
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
        self.assertNotEqual(None, attrs1_elem)
        self.assertEqual([None],
            [n.namespace_uri for n in attrs1_elem.attribute_nodes])
        attrs2_elem = wrapped_doc.find_first('Attrs2')
        self.assertEqual(['urn:custom'],
            [n.namespace_uri for n in attrs2_elem.attribute_nodes])

    def test_roundtrip(self):
        orig_xml = open(self.small_xml_file_path).read()
        doc = self.parse_string(orig_xml)
        roundtrip_xml = doc.doc_xml()
        if isinstance(self, TestLXMLParser):
            # lxml parser does not make it possible to retain semantically
            # unnecessary 'xmlns' namespace definitions in all elements.
            # It's not worth failing the roundtrip test just for this
            orig_xml = re.sub(
                '<NSDefaultExplicit xmlns="urn:default"/>',
                '<NSDefaultExplicit/>', orig_xml)
        self.assertEqual(orig_xml, roundtrip_xml)

    def test_unicode(self):
        # NOTE lxml doesn't support unicode namespace URIs, so we don't test that
        doc = self.parse_file(self.unicode_xml_file_path)
        self.assertEqual(u'جذر', doc.root.name)
        self.assertEqual(u'urn:default', doc.root.attributes[u'xmlns'])
        self.assertEqual(u'urn:custom', doc.root.attributes[u'xmlns:důl'])
        self.assertEqual(5, len(doc.find(ns_uri=u'urn:default')))
        self.assertEqual(3, len(doc.find(ns_uri=u'urn:custom')))
        self.assertEqual(u'1', doc.find_first(u'yếutố1').attributes[u'תכונה'])
        self.assertEqual(u'tvö', doc.find_first(u'yếutố2').attributes[u'důl:עודתכונה'])

class TestXmlDomParser(unittest.TestCase, BaseParserTest):

    def parse_string(self, xml_str):
        return parser.parse_string_xmldom(xml_str)

    def parse_file(self, xml_file):
        return parser.parse_file_xmldom(xml_file)


class TestLXMLParser(unittest.TestCase, BaseParserTest):

    def parse_string(self, xml_str):
        return parser.parse_string_lxml(xml_str)

    def parse_file(self, xml_file):
        return parser.parse_file_lxml(xml_file)
