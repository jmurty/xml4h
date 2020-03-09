# -*- coding: utf-8 -*-
import unittest
import functools
import six

import xml4h


class BaseWriterTest(object):

    @property
    def my_builder(self):
        return functools.partial(xml4h.build, adapter=self.adapter)

    def setUp(self):
        # Create test document
        self.builder = (
            self.my_builder('DocRoot')
                .element('Elem1').text(u'默认جذ').up()
                .element('Elem2'))
        # Handy IO writer
        self.iobytes = six.BytesIO()

    def test_write_defaults(self):
        """ Default write output is utf-8 with no pretty-printing """
        xml = (
            u'<?xml version="1.0" encoding="utf-8"?>'
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'
            )
        io_string = six.StringIO()
        self.builder.write_doc(io_string)
        if six.PY2:
            self.assertEqual(xml.encode('utf-8'), io_string.getvalue())
        else:
            self.assertEqual(xml, io_string.getvalue())

    def test_write_current_node_and_descendents(self):
        self.builder.dom_element.write(self.iobytes)
        self.assertEqual(b'<Elem2/>', self.iobytes.getvalue())

    def test_write_utf8_by_default(self):
        # Default write output is utf-8, with no pretty-printing
        xml = (
            u'<?xml version="1.0" encoding="utf-8"?>'
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'
            )
        self.builder.dom_element.write_doc(self.iobytes)
        self.assertEqual(xml.encode('utf-8'), self.iobytes.getvalue())

    def test_write_utf16(self):
        xml = (
            u'<?xml version="1.0" encoding="utf-16"?>'
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'
            )
        self.builder.dom_element.write_doc(self.iobytes, encoding='utf-16')
        self.assertEqual(xml.encode('utf-16'), self.iobytes.getvalue())

    def test_write_latin1_with_illegal_characters(self):
        self.assertRaises(UnicodeEncodeError,
            self.builder.dom_element.write_doc,
                self.iobytes, encoding='latin1', indent=2)

    def test_write_latin1(self):
        # Create latin1-friendly test document
        self.builder = (
            self.my_builder('DocRoot')
                .element('Elem1').text(u'Tést çæsè').up()
                .element('Elem2'))
        self.builder.dom_element.write_doc(self.iobytes, encoding='latin1')
        self.assertEqual(
            u'<?xml version="1.0" encoding="latin1"?>'
            u'<DocRoot>'
            u'<Elem1>Tést çæsè</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'.encode('latin1'),
            self.iobytes.getvalue())

    def test_with_no_encoding(self):
        """No encoding writes python unicode"""
        xml = (
            u'<?xml version="1.0"?>'
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'
            )
        io_string = six.StringIO()
        self.builder.dom_element.write_doc(io_string, encoding=None)
        # NOTE Exact test, no encoding of comparison XML doc string
        self.assertEqual(xml, io_string.getvalue())

    def test_omit_declaration(self):
        self.builder.dom_element.write_doc(self.iobytes,
                omit_declaration=True)
        self.assertEqual(
            u'<DocRoot>'
            u'<Elem1>默认جذ</Elem1>'
            u'<Elem2/>'
            u'</DocRoot>'.encode('utf-8'),
            self.iobytes.getvalue())

    def test_default_indent_and_newline(self):
        """Default indent of 4 spaces with newlines when indent=True"""
        self.builder.dom_element.write_doc(self.iobytes, indent=True)
        self.assertEqual(
            u'<?xml version="1.0" encoding="utf-8"?>\n'
            u'<DocRoot>\n'
            u'    <Elem1>默认جذ</Elem1>\n'
            u'    <Elem2/>\n'
            u'</DocRoot>\n'.encode('utf-8'),
            self.iobytes.getvalue())

    def test_custom_indent_and_newline(self):
        self.builder.dom_element.write_doc(self.iobytes,
            indent=8, newline='\t')
        self.assertEqual(
            u'<?xml version="1.0" encoding="utf-8"?>\t'
            u'<DocRoot>\t'
            u'        <Elem1>默认جذ</Elem1>\t'
            u'        <Elem2/>\t'
            u'</DocRoot>\t'.encode('utf-8'),
            self.iobytes.getvalue())


class TestXmlDomBuilder(BaseWriterTest, unittest.TestCase):
    """
    Tests building with the standard library xml.dom module, or with any
    library that augments/clobbers this module.
    """

    @property
    def adapter(self):
        return xml4h.XmlDomImplAdapter


class TestLXMLEtreeBuilder(BaseWriterTest, unittest.TestCase):
    """
    Tests building with the lxml (lxml.etree) library.
    """

    @property
    def adapter(self):
        if not xml4h.LXMLAdapter.is_available():
            self.skipTest("lxml library is not installed")
        return xml4h.LXMLAdapter


class TestElementTreeBuilder(BaseWriterTest, unittest.TestCase):
    """
    Tests building with the xml.etree.ElementTree library.
    """

    @property
    def adapter(self):
        if not xml4h.ElementTreeAdapter.is_available():
            self.skipTest(
                "ElementTree library is not installed or is outdated")
        return xml4h.ElementTreeAdapter


class TestElementTreeBuilder(BaseWriterTest, unittest.TestCase):
    """
    Tests building with the xml.etree.ElementTree library.
    """

    @property
    def adapter(self):
        if not xml4h.ElementTreeAdapter.is_available():
            self.skipTest(
                "cElementTree library is not installed or is outdated")
        return xml4h.ElementTreeAdapter
