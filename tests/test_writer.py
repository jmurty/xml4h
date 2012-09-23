# -*- coding: utf-8 name> -*-
import unittest
import functools
from StringIO import StringIO

import xml4h


class BaseWriterTest(object):

    def setUp(self):
        # Create test document
        self.builder = (
            self.my_builder('DocRoot')
                .element('Elem1').text(u'默认جذ').up()
                .element('Elem2'))
        # Handy IO writer
        self.iostr = StringIO()

    def test_write_current_node_and_descendents(self):
        self.builder.dom_element.write(self.iostr)
        self.assertEqual('<Elem2/>', self.iostr.getvalue())

    def test_write_utf8_by_default(self):
        # Default write output is utf-8, with no pretty-printing
        xml = (
            u'<?xml version="1.0" encoding="utf-8"?>'
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'
            )
        self.builder.dom_element.write_doc(self.iostr)
        self.assertEqual(xml.encode('utf-8'), self.iostr.getvalue())

    def test_write_utf16(self):
        xml = (
            u'<?xml version="1.0" encoding="utf-16"?>'
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'
            )
        self.builder.dom_element.write_doc(self.iostr, encoding='utf-16')
        self.assertEqual(xml.encode('utf-16'), self.iostr.getvalue())

    def test_write_latin1_with_illegal_characters(self):
        self.assertRaises(UnicodeEncodeError,
            self.builder.dom_element.write_doc,
                self.iostr, encoding='latin1', indent=2)

    def test_write_latin1(self):
        # Create latin1-friendly test document
        self.builder = (
            self.my_builder('DocRoot')
                .element('Elem1').text(u'Tést çæsè').up()
                .element('Elem2'))
        self.builder.dom_element.write_doc(self.iostr, encoding='latin1')
        self.assertEqual(
            u'<?xml version="1.0" encoding="latin1"?>'
            u'<DocRoot>'
            u'<Elem1>Tést çæsè</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'.encode('latin1'),
            self.iostr.getvalue())

    def test_with_no_encoding(self):
        """No encoding writes python unicode"""
        xml = (
            u'<?xml version="1.0"?>'
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'
            )
        self.builder.dom_element.write_doc(self.iostr, encoding=None)
        # NOTE Exact test, no encoding of comparison XML doc string
        self.assertEqual(xml, self.iostr.getvalue())

    def test_omit_declaration(self):
        self.builder.dom_element.write_doc(self.iostr,
                omit_declaration=True)
        self.assertEqual(
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'.encode('utf-8'),
            self.iostr.getvalue())

    def test_custom_indent_and_newline(self):
        self.builder.dom_element.write_doc(self.iostr,
            indent=8, newline='\t')
        self.assertEqual(
            u'<?xml version="1.0" encoding="utf-8"?>\t'
            u'<DocRoot>\t'
            u'        <Elem1>默认جذ</Elem1>\t'
            u'        <Elem2/>\t'
            u'</DocRoot>\t'.encode('utf-8'),
            self.iostr.getvalue())


class TestXmlDomBuilder(BaseWriterTest, unittest.TestCase):
    """
    Tests building with the standard library xml.dom module, or with any
    library that augments/clobbers this module.
    """

    @property
    def adapter(self):
        return xml4h.XmlDomImplAdapter

    @property
    def my_builder(self):
        return functools.partial(xml4h.build, adapter=self.adapter)


class TestLXMLEtreeBuilder(BaseWriterTest, unittest.TestCase):
    """
    Tests building with the lxml (lxml.etree) library.
    """

    @property
    def adapter(self):
        if not xml4h.LXMLAdapter.is_available():
            self.skipTest("lxml library is not installed")
        return xml4h.LXMLAdapter

    @property
    def my_builder(self):
        return functools.partial(xml4h.build, adapter=self.adapter)
