import unittest
import xml.dom

from xml4h.nodes import Element
from xml4h.impls.xml_dom import XmlDomImplWrapper

class BaseTestNodes(object):

    def test_wrap_document(self):
        wrapped_elem = XmlDomImplWrapper.wrap_document(self.doc)
        self.assertEqual(self.root_elem, wrapped_elem.impl_node)
        self.assertEqual('DocRoot', wrapped_elem.name)
        self.assertEqual(self.doc, wrapped_elem.impl_document)

    def test_wrap_node(self):
        # Wrap root node
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.root_elem)
        self.assertEqual(self.root_elem, wrapped_elem.impl_node)
        self.assertEqual('DocRoot', wrapped_elem.name)
        self.assertEqual(self.doc, wrapped_elem.impl_document)
        # Wrap a non-root node
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem3_second)
        self.assertEqual(self.elem3_second, wrapped_elem.impl_node)
        self.assertEqual('Element3', wrapped_elem.name)
        self.assertEqual('Element4', wrapped_elem.parent.name)

    def test_parent(self):
        # Root element has no parent
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.root_elem)
        self.assertEqual(None, wrapped_elem.parent)
        # Find parents of elements
        self.assertEqual(self.root_elem,
            XmlDomImplWrapper.wrap_node(self.elem1).parent.impl_node)
        self.assertEqual(self.elem3,
            XmlDomImplWrapper.wrap_node(self.elem2_second).parent.impl_node)
        # Parent of text node
        self.assertEqual(self.elem1,
            XmlDomImplWrapper.wrap_node(self.text_node).parent.impl_node)
        # Chain parent calls
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem3_second)
        self.assertEqual(self.root_elem, wrapped_elem.parent.parent.impl_node)

    def test_find_methods(self):
        # Find all elements in document
        elems = self.wrapped_root.find(whole_document=True)
        self.assertEqual(7, len(elems))
        elems = self.wrapped_root.doc_find()
        self.assertEqual(7, len(elems))
        # Find all element descendants of root
        elems = self.wrapped_root.find()
        self.assertEqual(6, len(elems))
        # Find when no element names match
        elems = self.wrapped_root.find('NoMatchingName')
        self.assertEqual(0, len(elems))
        self.assertEqual([], elems)
        # Find non-namespaced element
        elems = self.wrapped_root.find('Element1')
        self.assertEqual(1, len(elems))
        self.assertIsInstance(elems[0], Element)
        # Find multiple non-namespaced elements
        elems = self.wrapped_root.find('Element2')
        self.assertEqual(2, len(elems))
        self.assertIsInstance(elems[0], Element)
        self.assertIsInstance(elems[1], Element)
        self.assertEqual('DocRoot', elems[0].parent.name)
        self.assertEqual('Element3', elems[1].parent.name)
        # Find namespaced elements (only 1 Element3 in each namespace)
        elems = self.wrapped_root.find('Element3', ns_uri='urn:ns1')
        self.assertEqual(1, len(elems))
        self.assertEqual('DocRoot', elems[0].parent.name)
        elems = self.wrapped_root.find('Element3', ns_uri='urn:ns2')
        self.assertEqual(1, len(elems))
        self.assertEqual('Element4', elems[0].parent.name)
        # Non-namespaced find will find elements across namespaces
        elems = self.wrapped_root.find('Element3')
        self.assertEqual(2, len(elems))
        # Find only elements in a given namespace
        elems = self.wrapped_root.find(ns_uri='urn:ns1')
        self.assertEqual(2, len(elems))
        self.assertEqual('Element3', elems[0].name)
        self.assertEqual('DocRoot', elems[0].parent.name)
        self.assertEqual('Element4', elems[1].name)
        elems = self.wrapped_root.find(ns_uri='urn:ns2')
        self.assertEqual(1, len(elems))
        self.assertEqual('Element3', elems[0].name)
        self.assertEqual('Element4', elems[0].parent.name)
        # Chain finds
        self.wrapped_root.find('Element3')[0].find
        # Find first only
        self.assertEqual(None, self.wrapped_root.find_first('NoMatchingName'))
        self.assertEqual(self.elem1,
                self.wrapped_root.find_first('Element1').impl_node)
        self.assertEqual(self.elem2,
                self.wrapped_root.find_first('Element2').impl_node)


class TestMinidomNodes(BaseTestNodes, unittest.TestCase):

    def setUp(self):
        # Build a DOM using minidom for testing
        factory = xml.dom.getDOMImplementation('minidom')
        ns_uri = 'urn:test'
        doctype = None
        doc = factory.createDocument(ns_uri, 'DocRoot', doctype)
        self.root_elem = doc.firstChild
        self.elem1 = doc.createElement('Element1')
        self.elem2 = doc.createElement('Element2')
        self.elem3 = doc.createElementNS('urn:ns1', 'Element3')
        self.elem4 = doc.createElementNS('urn:ns1', 'Element4')
        self.elem2_second = doc.createElement('Element2')
        self.elem3_second = doc.createElementNS('urn:ns2', 'Element3')
        self.text_node = doc.createTextNode('Some text')
        doc.documentElement.appendChild(self.elem1)
        doc.documentElement.appendChild(self.elem2)
        doc.documentElement.appendChild(self.elem3)
        doc.documentElement.appendChild(self.elem4)
        self.elem1.appendChild(self.text_node)
        self.elem3.appendChild(self.elem2_second)
        self.elem4.appendChild(self.elem3_second)
        self.doc = doc
        self.wrapped_root = XmlDomImplWrapper.wrap_document(doc)

