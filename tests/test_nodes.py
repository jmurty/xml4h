import unittest
import xml.dom

from xml4h import nodes
from xml4h.impls.xml_dom import XmlDomImplWrapper

class BaseTestNodes(object):

    def test_wrap_document(self):
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.root_elem)
        self.assertEqual(self.root_elem, wrapped_elem.impl_node)
        self.assertEqual('DocRoot', wrapped_elem.name)
        self.assertEqual(self.doc, wrapped_elem.impl_document)

    def test_wrap_node_and_is_type_methods(self):
        # Wrap root element
        wrapped_node = XmlDomImplWrapper.wrap_node(self.root_elem)
        self.assertEqual(self.root_elem, wrapped_node.impl_node)
        self.assertEqual('DocRoot', wrapped_node.name)
        self.assertEqual(self.doc, wrapped_node.impl_document)
        self.assertTrue(wrapped_node.is_type(nodes.ELEMENT_NODE))
        self.assertTrue(wrapped_node.is_element)
        # Wrap a non-root element
        wrapped_node = XmlDomImplWrapper.wrap_node(self.elem3_second)
        self.assertEqual(self.elem3_second, wrapped_node.impl_node)
        self.assertEqual('ns2:Element3', wrapped_node.name)
        self.assertEqual('Element4', wrapped_node.parent.name)
        self.assertTrue(wrapped_node.is_type(nodes.ELEMENT_NODE))
        self.assertTrue(wrapped_node.is_element)
        # Test node types
        wrapped_node = XmlDomImplWrapper.wrap_node(self.text_node)
        self.assertIsInstance(wrapped_node, nodes.Text)
        self.assertTrue(wrapped_node.is_type(nodes.TEXT_NODE))
        self.assertTrue(wrapped_node.is_text)
        wrapped_node = XmlDomImplWrapper.wrap_node(self.cdata_node)
        self.assertIsInstance(wrapped_node, nodes.CDATA)
        self.assertTrue(wrapped_node.is_type(nodes.CDATA_NODE))
        self.assertTrue(wrapped_node.is_cdata)
        wrapped_node =XmlDomImplWrapper.wrap_node(self.comment_node)
        self.assertIsInstance(wrapped_node, nodes.Comment)
        self.assertTrue(wrapped_node.is_type(nodes.COMMENT_NODE))
        self.assertTrue(wrapped_node.is_comment)
        wrapped_node = XmlDomImplWrapper.wrap_node(self.instruction_node)
        self.assertIsInstance(wrapped_node, nodes.ProcessingInstruction)
        self.assertTrue(wrapped_node.is_type(nodes.PROCESSING_INSTRUCTION_NODE))
        self.assertTrue(wrapped_node.is_processing_instruction)

    def test_parent(self):
        # Document node has no parent
        wrapped_doc = XmlDomImplWrapper.wrap_node(self.doc)
        self.assertEqual(None, wrapped_doc.parent)
        # Root element has document as parent
        self.assertIsInstance(self.wrapped_root.parent, nodes.Document)
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

    def test_children(self):
        self.assertEquals(self.elem1, self.wrapped_root.children[0].impl_node)
        self.assertEquals(['Element1', 'Element2', 'Element3', 'Element4'],
            [n.name for n in self.wrapped_root.children])
        self.assertEquals(['Element2'],
            [n.name for n in self.wrapped_root.find_first('Element3').children])

    def test_siblings(self):
        wrapped_node = self.wrapped_root.children[1]
        self.assertEqual(['Element1', 'Element3', 'Element4'],
            [n.name for n in wrapped_node.siblings])
        self.assertEqual(['Element1'],
            [n.name for n in wrapped_node.siblings_before])
        self.assertEqual(['Element3', 'Element4'],
            [n.name for n in wrapped_node.siblings_after])
        # Empty list if finding siblings beyond beginning/end of nodes
        self.assertEqual([], self.wrapped_root.children[0].siblings_before)
        self.assertEqual([], self.wrapped_root.children[-1].siblings_after)

    def test_namespace_data(self):
        # Namespace data for element without namespace
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem1)
        self.assertEqual(None, wrapped_elem.namespace_uri)
        self.assertEqual('Element1', wrapped_elem.name)
        self.assertEqual(None, wrapped_elem.prefix)
        self.assertEqual('Element1', wrapped_elem.local_name)
        # Namespace data for ns element without prefix
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem3)
        self.assertEqual('urn:ns1', wrapped_elem.namespace_uri)
        self.assertEqual('Element3', wrapped_elem.name)
        self.assertEqual(None, wrapped_elem.prefix)
        self.assertEqual('Element3', wrapped_elem.local_name)
        # Namespace data for ns element with prefix
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem3_second)
        self.assertEqual('urn:ns2', wrapped_elem.namespace_uri)
        self.assertEqual('ns2:Element3', wrapped_elem.name)
        self.assertEqual('ns2', wrapped_elem.prefix)
        self.assertEqual('Element3', wrapped_elem.local_name)
        # Namespace data for attribute node without namespace
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem1)
        self.assertEqual(None, wrapped_elem.attribute_nodes[0].namespace_uri)
        self.assertEqual('a', wrapped_elem.attribute_nodes[0].name)
        self.assertEqual(None, wrapped_elem.attribute_nodes[0].prefix)
        self.assertEqual('a', wrapped_elem.attribute_nodes[0].local_name)
        # Namespace data for attribute node with namespace
        self.assertEqual('urn:ns1', wrapped_elem.attribute_nodes[1].namespace_uri)
        self.assertEqual('ns1:b', wrapped_elem.attribute_nodes[1].name)
        self.assertEqual('ns1', wrapped_elem.attribute_nodes[1].prefix)
        self.assertEqual('b', wrapped_elem.attribute_nodes[1].local_name)
        # Namespace data for attribute dict without namespace
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem1)
        self.assertEqual(None, wrapped_elem.attributes.namespace_uri('a'))
        # Namespace data for attribute dict with namespace
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem1)
        self.assertEqual('urn:ns1', wrapped_elem.attributes.namespace_uri('ns1:b'))

    def test_name(self):
        wrapped_node = XmlDomImplWrapper.wrap_node(self.elem1)
        self.assertEqual('Element1', wrapped_node.name)
        attribute_node = wrapped_node.attribute_nodes[0]
        self.assertEqual('a', attribute_node.name)
        wrapped_node = XmlDomImplWrapper.wrap_node(self.text_node)
        self.assertEqual('#text', wrapped_node.name)
        wrapped_node = XmlDomImplWrapper.wrap_node(self.cdata_node)
        self.assertEqual('#cdata-section', wrapped_node.name)
        wrapped_node =XmlDomImplWrapper.wrap_node(self.comment_node)
        self.assertEqual('#comment', wrapped_node.name)
        wrapped_node = XmlDomImplWrapper.wrap_node(self.instruction_node)
        self.assertEqual(wrapped_node.target, wrapped_node.name)

    def test_attributes(self):
        # Non-element nodes don't have attributes
        self.assertEqual(None, self.wrapped_doc.attributes)
        self.assertEqual(None, self.wrapped_text.attributes)
        self.assertEqual(None, self.wrapped_doc.attribute_nodes)
        self.assertEqual(None, self.wrapped_text.attribute_nodes)
        # Get element's attribute nodes
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem1)
        attr_nodes = wrapped_elem.attribute_nodes
        self.assertEqual(2, len(attr_nodes))
        self.assertEqual(['a', 'ns1:b'], [a.name for a in attr_nodes])
        self.assertEqual(['1', '2'], [a.value for a in attr_nodes])
        self.assertEqual(['a', 'b'], [a.local_name for a in attr_nodes])
        self.assertEqual([None, 'ns1'], [a.prefix for a in attr_nodes])
        self.assertEqual([None, 'urn:ns1'], [a.ns_uri for a in attr_nodes])
        # Get element's attributes dict
        wrapped_elem = XmlDomImplWrapper.wrap_node(self.elem1)
        attrs_dict = wrapped_elem.attributes
        self.assertEqual(2, len(attrs_dict))
        self.assertEqual(['a', 'ns1:b'], attrs_dict.keys())
        self.assertEqual(['1', '2'], attrs_dict.values())
        # Set/change attributes via element methods
        wrapped_elem.set_attributes({'a': 10, 'c': 3})
        self.assertEqual(['10', '3', '2'],
            [a.value for a in wrapped_elem.attribute_nodes])
        # Set attributes via dict assignment (pre-existing attributes are deleted)
        wrapped_elem.attributes = {
            'a': 100,  # effectively replaces prior 'a' attribute
            ('ns1:d', 'urn:ns1'): -3,  # attribute with namespace
            }
        self.assertEqual(['a', 'ns1:d'],
            [a.name for a in wrapped_elem.attribute_nodes])
        self.assertEqual('100', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns1:d'])
        # Set/replace attributes via dict modification
        wrapped_elem.attributes['a'] = 200
        wrapped_elem.attributes['e'] = 'E'
        self.assertEqual(['a', 'e', 'ns1:d'],
            [a.name for a in wrapped_elem.attribute_nodes])
        self.assertEqual('200', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns1:d'])
        self.assertEqual('E', wrapped_elem.attributes['e'])
        # In-place modifications to attribute reflected in element
        attr_dict = wrapped_elem.attributes
        attr_dict['a'] = 'A' # Modify
        attr_dict['b'] = 'B' # Add
        del(attr_dict['e']) # Delete
        self.assertEqual(['a', 'b', 'ns1:d'],
            [a.name for a in wrapped_elem.attribute_nodes])
        self.assertEqual('A', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns1:d'])
        self.assertEqual(None, wrapped_elem.attributes['e'])
        # Contains works on attribute dict
        self.assertTrue('a' in wrapped_elem.attributes)
        self.assertFalse('e' in wrapped_elem.attributes)

    def test_element_text(self):
        # Get text on element
        wrapped_node = XmlDomImplWrapper.wrap_node(self.elem1)
        self.assertEqual('Some text', wrapped_node.text)
        # Set text on element
        wrapped_node.text = 'Different text'
        self.assertEqual('Different text', wrapped_node.text)
        self.assertEqual(
            wrapped_node.children[0].value,
            wrapped_node.children[0].impl_node.nodeValue)
        # Unset text on element (removes any text children)
        wrapped_node.text = None
        self.assertEqual(None, wrapped_node.text)
        self.assertEqual([], wrapped_node.children)

    def test_delete(self):
        # Remove single Element using delete() method
        self.assertEqual(
            ['Element1', 'Element2', 'Element3', 'Element4'],
            [n.name for n in self.wrapped_root.children])
        self.wrapped_root.children[0].delete()
        self.assertEqual(
            ['Element2', 'Element3', 'Element4'],
            [n.name for n in self.wrapped_root.children])
        self.assertEqual(6, len(self.wrapped_root.doc_find()))
        # Remove element with child elements using __del__()
        # TODO Implement __del__()
#        del(self.wrapped_root.children[2])
#        self.assertEqual(
#            ['Element2', 'Element3'],
#            [n.name for n in self.wrapped_root.children])
#        self.assertEqual(4, len(self.wrapped_root.doc_find()))

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
        self.assertIsInstance(elems[0], nodes.Element)
        # Find multiple non-namespaced elements
        elems = self.wrapped_root.find('Element2')
        self.assertEqual(2, len(elems))
        self.assertIsInstance(elems[0], nodes.Element)
        self.assertIsInstance(elems[1], nodes.Element)
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
        self.assertEqual('ns2:Element3', elems[0].name)
        self.assertEqual('Element3', elems[0].local_name)
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
        self.elem1.setAttribute('a', '1')
        self.elem1.setAttributeNS('urn:ns1', 'ns1:b', '2')
        self.elem2 = doc.createElement('Element2')
        self.elem3 = doc.createElementNS('urn:ns1', 'Element3')
        self.elem4 = doc.createElementNS('urn:ns1', 'Element4')
        self.elem2_second = doc.createElement('Element2')
        self.elem3_second = doc.createElementNS('urn:ns2', 'ns2:Element3')
        self.text_node = doc.createTextNode('Some text')
        self.cdata_node = doc.createCDATASection('Some cdata')
        self.comment_node = doc.createComment('A comment')
        self.instruction_node = doc.createProcessingInstruction(
            'pi-target', 'pi-data')
        doc.documentElement.appendChild(self.elem1)
        doc.documentElement.appendChild(self.elem2)
        doc.documentElement.appendChild(self.elem3)
        doc.documentElement.appendChild(self.elem4)
        self.elem1.appendChild(self.text_node)
        self.elem2.appendChild(self.cdata_node)
        self.elem3.appendChild(self.elem2_second)
        self.elem2_second.appendChild(self.comment_node)
        self.elem4.appendChild(self.elem3_second)
        self.elem3_second.appendChild(self.instruction_node)
        self.doc = doc
        self.wrapped_doc = XmlDomImplWrapper.wrap_document(doc)
        self.wrapped_root = self.wrapped_doc.root
        self.wrapped_text = XmlDomImplWrapper.wrap_node(self.text_node)

