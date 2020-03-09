# -*- coding: utf-8 -*-
import six
import unittest
import os
import re

import xml4h


class TestParserBasics(unittest.TestCase):

    @property
    def small_xml_file_path(self):
        return os.path.join(
            os.path.dirname(__file__), 'data/example_doc.small.xml')

    def test_parse_with_default_parser(self):
        # Explicit use of default/best adapter
        dom = xml4h.parse(self.small_xml_file_path, adapter=xml4h.best_adapter)
        self.assertEqual(8, len(dom.find()))
        # Implicit use of default/best adapter
        dom = xml4h.parse(self.small_xml_file_path)
        self.assertEqual(8, len(dom.find()))
        self.assertEqual(xml4h.best_adapter, dom.adapter_class)


class BaseParserTest(object):
    """
    Tests to exercise parsing across all xml4h implementations.
    """

    @property
    def small_xml_file_path(self):
        return os.path.join(
            os.path.dirname(__file__), 'data/example_doc.small.xml')

    @property
    def unicode_xml_file_path(self):
        return os.path.join(
            os.path.dirname(__file__), 'data/example_doc.unicode.xml')

    def parse(self, xml_str):
        return xml4h.parse(xml_str, adapter=self.adapter)

    def test_auto_detect_filename_or_xml_data(self):
        # String with a '<' is parsed as literal XML data
        dom = self.parse('\n\n\t<MyDoc><Elem1>content</Elem1></MyDoc>')
        self.assertEqual(2, len(dom.find()))
        # String without a '<' is treated as a file path -- invalid path
        self.assertRaises(IOError, self.parse, 'not/a/real/file/path')
        # String without a '<' is treated as a file path -- valid path
        self.parse(self.small_xml_file_path)

    def test_parse_file(self):
        wrapped_doc = self.parse(self.small_xml_file_path)
        self.assertIsInstance(wrapped_doc, xml4h.nodes.Document)
        self.assertEqual(8, len(wrapped_doc.find()))
        # Check element namespaces
        self.assertEqual(
            ['DocRoot', 'NSDefaultImplicit', 'NSDefaultExplicit',
             'Attrs1', 'Attrs2'],
            [n.name for n in wrapped_doc.find(ns_uri='urn:default')])
        self.assertEqual(
            ['urn:custom', 'urn:custom', 'urn:custom'],
            [n.namespace_uri for n in wrapped_doc.find(ns_uri='urn:custom')])
        # We test local name, not full name, here as different XML libraries
        # retain (or not) different literal element prefixes differently.
        self.assertEqual(
            ['NSCustomExplicit',
             'NSCustomWithPrefixImplicit',
             'NSCustomWithPrefixExplicit'],
            [n.local_name for n in wrapped_doc.find(ns_uri='urn:custom')])
        # Check namespace attributes
        self.assertEqual(
            [xml4h.nodes.Node.XMLNS_URI, xml4h.nodes.Node.XMLNS_URI],
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
        # We discard semantically unnecessary namespace prefixes on
        # element names.
        orig_xml = re.sub(
            '<myns:NSCustomWithPrefixExplicit xmlns="urn:custom"/>',
            '<NSCustomWithPrefixExplicit xmlns="urn:custom"/>', orig_xml)
        if self.adapter == xml4h.LXMLAdapter:
            # lxml parser does not make it possible to retain semantically
            # unnecessary 'xmlns' namespace definitions in all elements.
            # It's not worth failing the roundtrip test just for this
            orig_xml = re.sub(
                '<NSDefaultExplicit xmlns="urn:default"/>',
                '<NSDefaultExplicit/>', orig_xml)
        doc = self.parse(self.small_xml_file_path)
        roundtrip_xml = doc.xml_doc()
        self.assertEqual(six.text_type(orig_xml), roundtrip_xml)

    def test_unicode(self):
        # NOTE lxml doesn't support unicode namespace URIs?
        doc = self.parse(self.unicode_xml_file_path)
        self.assertEqual(u'جذر', doc.root.name)
        self.assertEqual(u'urn:default', doc.root.attributes['xmlns'])
        self.assertEqual(u'urn:custom', doc.root.attributes[u'xmlns:důl'])
        self.assertEqual(5, len(doc.find(ns_uri=u'urn:default')))
        self.assertEqual(3, len(doc.find(ns_uri=u'urn:custom')))
        self.assertEqual(u'1', doc.find_first(u'yếutố1').attributes[u'תכונה'])
        self.assertEqual(u'tvö',
            doc.find_first(u'yếutố2').attributes[u'důl:עודתכונה'])


class TestXmlDomParser(unittest.TestCase, BaseParserTest):

    @property
    def adapter(self):
        return xml4h.XmlDomImplAdapter


class TestLXMLEtreeParser(unittest.TestCase, BaseParserTest):

    @property
    def adapter(self):
        if not xml4h.LXMLAdapter.is_available():
            self.skipTest("lxml library is not installed")
        return xml4h.LXMLAdapter


class TestElementTreeEtreeParser(unittest.TestCase, BaseParserTest):

    @property
    def adapter(self):
        if not xml4h.ElementTreeAdapter.is_available():
            self.skipTest(
                "ElementTree library is not installed or is outdated")
        return xml4h.ElementTreeAdapter


class TestcElementTreeEtreeParser(unittest.TestCase, BaseParserTest):

    @property
    def adapter(self):
        if not xml4h.cElementTreeAdapter.is_available():
            self.skipTest(
                "cElementTree library is not installed or is outdated")
        return xml4h.cElementTreeAdapter
