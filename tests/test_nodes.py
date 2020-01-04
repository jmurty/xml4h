# -*- coding: utf-8 -*-
import types
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import xml4h


class BaseTestNodes(object):

    def test_wrap_document(self):
        wrapped_elem = self.adapter_class.wrap_node(self.root_elem, self.doc)
        self.assertEqual(self.root_elem, wrapped_elem.impl_node)
        self.assertEqual('DocRoot', wrapped_elem.name)
        self.assertEqual(self.doc, wrapped_elem.impl_document)

    def test_wrap_node_and_is_type_methods(self):
        # Wrap root element
        wrapped_node = self.adapter_class.wrap_node(self.root_elem, self.doc)
        self.assertEqual(self.root_elem, wrapped_node.impl_node)
        self.assertEqual('DocRoot', wrapped_node.name)
        self.assertEqual(self.doc, wrapped_node.impl_document)
        self.assertTrue(wrapped_node.is_type(xml4h.nodes.ELEMENT_NODE))
        self.assertTrue(wrapped_node.is_element)
        # Wrap a non-root element
        wrapped_node = self.adapter_class.wrap_node(self.elem3_second, self.doc)
        self.assertEqual(self.elem3_second, wrapped_node.impl_node)
        self.assertEqual('ns2:Element3', wrapped_node.name)
        self.assertEqual('Element4', wrapped_node.parent.name)
        self.assertTrue(wrapped_node.is_type(xml4h.nodes.ELEMENT_NODE))
        self.assertTrue(wrapped_node.is_element)
        # Test node types
        wrapped_node = self.adapter_class.wrap_node(self.text_node, self.doc)
        self.assertIsInstance(wrapped_node, xml4h.nodes.Text)
        self.assertTrue(wrapped_node.is_type(xml4h.nodes.TEXT_NODE))
        self.assertTrue(wrapped_node.is_text)
        wrapped_node = self.adapter_class.wrap_node(self.cdata_node, self.doc)
        self.assertIsInstance(wrapped_node, xml4h.nodes.CDATA)
        self.assertTrue(wrapped_node.is_type(xml4h.nodes.CDATA_NODE))
        self.assertTrue(wrapped_node.is_cdata)
        wrapped_node = self.adapter_class.wrap_node(self.comment_node, self.doc)
        self.assertIsInstance(wrapped_node, xml4h.nodes.Comment)
        self.assertTrue(wrapped_node.is_type(xml4h.nodes.COMMENT_NODE))
        self.assertTrue(wrapped_node.is_comment)
        wrapped_node = self.adapter_class.wrap_node(
            self.instruction_node, self.doc)
        self.assertIsInstance(
            wrapped_node, xml4h.nodes.ProcessingInstruction)
        self.assertTrue(
            wrapped_node.is_type(xml4h.nodes.PROCESSING_INSTRUCTION_NODE))
        self.assertTrue(wrapped_node.is_processing_instruction)

    def test_wrap_node_reuses_adapter_when_provided(self):
        # Wrap root element, creates a new adapter instance if none provided
        wrapped_root = self.adapter_class.wrap_node(self.root_elem, self.doc)
        wrapped_node = self.adapter_class.wrap_node(self.elem3_second, self.doc)
        self.assertNotEqual(wrapped_root.adapter, wrapped_node.adapter)
        # Wrap root element, reuses adapter instance if provided
        wrapped_node = self.adapter_class.wrap_node(
            self.elem3_second, self.doc, wrapped_root.adapter)
        self.assertEqual(wrapped_root.adapter, wrapped_node.adapter)

    def test_parent(self):
        # Document node has no parent
        xml4h_doc = self.adapter_class.wrap_node(self.doc, self.doc)
        self.assertEqual(None, xml4h_doc.parent)
        # Root element has document as parent
        self.assertIsInstance(self.xml4h_root.parent, xml4h.nodes.Document)
        # Find parents of elements
        self.assertEqual(self.root_elem,
            self.adapter_class.wrap_node(self.elem1, self.doc).parent.impl_node)
        self.assertEqual(self.elem3,
            self.adapter_class.wrap_node(
                self.elem2_second, self.doc).parent.impl_node)
        # Parent of text node (Text not stored as node in lxml/ElementTree)
        if not isinstance(self, (TestLXMLNodes, TestElementTreeNodes)):
            self.assertEqual(self.elem1,
                self.adapter_class.wrap_node(
                    self.text_node, self.doc).parent.impl_node)
        # Chain parent calls
        wrapped_elem = self.adapter_class.wrap_node(self.elem3_second, self.doc)
        self.assertEqual(self.root_elem, wrapped_elem.parent.parent.impl_node)

    def test_ancestors(self):
        # Document node has no ancestors
        xml4h_doc = self.adapter_class.wrap_node(self.doc, self.doc)
        self.assertEqual([], xml4h_doc.ancestors)
        # Find ancestors of elements
        self.assertEqual(['DocRoot'],
            [a.name for a in
             self.adapter_class.wrap_node(self.elem1, self.doc).ancestors
             if a.is_element])
        self.assertEqual(['Element4', 'DocRoot'],
            [a.name for a in
             self.adapter_class.wrap_node(self.elem3_second, self.doc).ancestors
             if a.is_element])
        # Document root node (not Element) is included in ancestors list
        self.assertTrue(
            self.adapter_class.wrap_node(
                self.elem3_second, self.doc).ancestors[-1].is_document)

    def test_children_attribute(self):
        self.assertEqual(self.elem1, self.xml4h_root.children[0].impl_node)
        self.assertEqual([u'元素1', 'Element2', 'Element3', 'Element4'],
            [n.name for n in self.xml4h_root.children])
        self.assertEqual(['Element2'],
            [n.name for n in self.xml4h_root.find_first('Element3').children])

    def test_children_nodelist_callable(self):
        """Use callable feature of children attribute's returned NodeList"""
        self.assertEqual(self.elem1, self.xml4h_root.children()[0].impl_node)
        self.assertEqual([u'元素1', 'Element2', 'Element3', 'Element4'],
            [n.name for n in self.xml4h_root.children()])
        self.assertEqual(['Element2'],
            [n.name for n in
                self.xml4h_root.find_first('Element3').children()])
        # Filter children by name
        self.assertEqual(['Element2'],
            [n.name for n in self.xml4h_root.children(name='Element2')])
        # Filter children by local name
        self.assertEqual(['Element2'],
            [n.name for n in self.xml4h_root.children(local_name='Element2')])
        # Filter children by namespace
        self.assertEqual(['Element3', 'Element4'],
            [n.name for n in self.xml4h_root.children(ns_uri='urn:ns1')])
        # Filter by node type
        self.assertEqual([],
            [n.name for n in self.xml4h_root.children(
                                  node_type=xml4h.nodes.Text)])
        self.assertEqual([u'元素1', 'Element2', 'Element3', 'Element4'],
            [n.name for n in self.xml4h_root.children(
                                  node_type=xml4h.nodes.ELEMENT_NODE)])
        self.assertEqual([u'元素1', 'Element2', 'Element3', 'Element4'],
            [n.name for n in self.xml4h_root.children(
                                  node_type=xml4h.nodes.Element)])
        # Filter by arbitrary function
        fn = lambda x: x.name[-1] in ('1', '3')
        self.assertEqual([u'元素1', 'Element3'],
            [n.name for n in self.xml4h_root.children(filter_fn=fn)])
        # Return first result only via `first_only` flag
        self.assertEqual('Element3',
            self.xml4h_root.children(ns_uri='urn:ns1', first_only=True).name)
        self.assertEqual(None,
            self.xml4h_root.children(ns_uri='urn:wrong', first_only=True))
        # Return first result only via `first` attribute on children
        self.assertEqual('Element3',
            self.xml4h_root.children(ns_uri='urn:ns1').first.name)
        self.assertEqual(None,
            self.xml4h_root.children(ns_uri='urn:wrong').first)
        # Return first result only via `child` method
        self.assertEqual('Element3',
            self.xml4h_root.child(ns_uri='urn:ns1').name)
        self.assertEqual(None,
            self.xml4h_root.child(ns_uri='urn:wrong'))

    def test_siblings(self):
        wrapped_node = self.xml4h_root.children[1]
        self.assertEqual([u'元素1', 'Element3', 'Element4'],
            [n.name for n in wrapped_node.siblings])
        self.assertEqual([u'元素1'],
            [n.name for n in wrapped_node.siblings_before])
        self.assertEqual(['Element3', 'Element4'],
            [n.name for n in wrapped_node.siblings_after])
        # Empty list if finding siblings beyond beginning/end of nodes
        self.assertEqual([], self.xml4h_root.children[0].siblings_before)
        self.assertEqual([], self.xml4h_root.children[-1].siblings_after)

    def test_namespace_data(self):
        # Namespace data for element without namespace
        wrapped_elem = self.adapter_class.wrap_node(self.elem1, self.doc)
        self.assertEqual(None, wrapped_elem.namespace_uri)
        self.assertEqual(u'元素1', wrapped_elem.name)
        self.assertEqual(None, wrapped_elem.prefix)
        self.assertEqual(u'元素1', wrapped_elem.local_name)
        # Namespace data for ns element without prefix
        wrapped_elem = self.adapter_class.wrap_node(self.elem3, self.doc)
        self.assertEqual('urn:ns1', wrapped_elem.namespace_uri)
        self.assertEqual('Element3', wrapped_elem.name)
        self.assertEqual(None, wrapped_elem.prefix)
        self.assertEqual('Element3', wrapped_elem.local_name)
        # Namespace data for ns element with prefix
        wrapped_elem = self.adapter_class.wrap_node(self.elem3_second, self.doc)
        self.assertEqual('urn:ns2', wrapped_elem.namespace_uri)
        self.assertEqual('ns2:Element3', wrapped_elem.name)
        self.assertEqual('ns2', wrapped_elem.prefix)
        self.assertEqual('Element3', wrapped_elem.local_name)
        # Namespace data for attribute node without namespace
        wrapped_elem = self.adapter_class.wrap_node(self.elem1, self.doc)
        self.assertEqual(None, wrapped_elem.attribute_nodes[0].namespace_uri)
        self.assertEqual('a', wrapped_elem.attribute_nodes[0].name)
        self.assertEqual(None, wrapped_elem.attribute_nodes[0].prefix)
        self.assertEqual('a', wrapped_elem.attribute_nodes[0].local_name)
        # Namespace data for attribute node with namespace
        self.assertEqual('urn:ns1',
            wrapped_elem.attribute_nodes[1].namespace_uri)
        self.assertEqual('ns1:b', wrapped_elem.attribute_nodes[1].name)
        self.assertEqual('ns1', wrapped_elem.attribute_nodes[1].prefix)
        self.assertEqual('b', wrapped_elem.attribute_nodes[1].local_name)
        # Namespace data for attribute dict without namespace
        wrapped_elem = self.adapter_class.wrap_node(self.elem1, self.doc)
        self.assertEqual(None, wrapped_elem.attributes.namespace_uri('a'))
        # Namespace data for attribute dict with namespace
        wrapped_elem = self.adapter_class.wrap_node(self.elem1, self.doc)
        self.assertEqual('urn:ns1',
            wrapped_elem.attributes.namespace_uri('ns1:b'))

    def test_name(self):
        wrapped_node = self.adapter_class.wrap_node(self.elem1, self.doc)
        self.assertEqual(u'元素1', wrapped_node.name)
        attribute_node = wrapped_node.attribute_nodes[0]
        self.assertEqual('a', attribute_node.name)
        wrapped_node = self.adapter_class.wrap_node(self.text_node, self.doc)
        self.assertEqual('#text', wrapped_node.name)
        wrapped_node = self.adapter_class.wrap_node(self.cdata_node, self.doc)
        self.assertEqual('#cdata-section', wrapped_node.name)
        wrapped_node = self.adapter_class.wrap_node(self.comment_node, self.doc)
        self.assertEqual('#comment', wrapped_node.name)
        wrapped_node = self.adapter_class.wrap_node(
            self.instruction_node, self.doc)
        self.assertEqual(wrapped_node.target, wrapped_node.name)

    def test_attributes(self):
        # Non-element nodes don't have attributes
        self.assertEqual(None, self.xml4h_doc.attributes)
        self.assertEqual(None, self.xml4h_doc.attribute_nodes)
        self.assertEqual(None, self.xml4h_text.attributes)
        self.assertEqual(None, self.xml4h_text.attribute_nodes)
        # Get element's attribute nodes
        wrapped_elem = self.adapter_class.wrap_node(self.elem1, self.doc)
        attr_nodes = wrapped_elem.attribute_nodes
        self.assertEqual(
            ['a', 'ns1:b', 'xmlns:ns1'],
            [a.name for a in attr_nodes])
        self.assertEqual(
            ['1', '2', 'urn:ns1'],
            [a.value for a in attr_nodes])
        self.assertEqual(
            ['a', 'b', 'ns1'],
            [a.local_name for a in attr_nodes])
        self.assertEqual(
            [None, 'ns1', 'xmlns'],
            [a.prefix for a in attr_nodes])
        self.assertEqual(
            [None, 'urn:ns1', 'http://www.w3.org/2000/xmlns/'],
            [a.ns_uri for a in attr_nodes])
        # Get element's attributes dict
        wrapped_elem = self.adapter_class.wrap_node(self.elem1, self.doc)
        attrs_dict = wrapped_elem.attributes
        self.assertEqual(
            sorted(['a', 'ns1:b', 'xmlns:ns1']),
            sorted(attrs_dict.keys()))
        self.assertEqual(
            ['1', '2', 'urn:ns1'],
            [attrs_dict['a'], attrs_dict['ns1:b'], attrs_dict['xmlns:ns1']])
        # Set/change attributes via element methods
        wrapped_elem.set_attributes({'a': 10, 'c': 3})
        self.assertEqual(
            sorted(['a', 'c', 'ns1:b', 'xmlns:ns1']),
            sorted(attrs_dict.keys()))
        self.assertEqual(
            ['10', '3', '2', 'urn:ns1'],
            [a.value for a in wrapped_elem.attribute_nodes])
        # Set attributes via dict assignment (pre-existing attrs are deleted)
        wrapped_elem.attributes = {
            'a': 100,  # effectively replaces prior 'a' attribute
            'xmlns:ns2': 'urn:ns2',  # namespace definition
            'ns2:d': -3,  # attribute with namespace prefix
            '{urn:ns2}x': -5  # attribute with etree-style namespace URI
            }
        if self.adapter_class == xml4h.LXMLAdapter:
            # Cannot delete pre-existing namespaces in lxml. For similar
            # subsequent tests we use subset comparisons
            self.assertEqual(['a', 'ns2:d', 'ns2:x',
                'xmlns:ns1',  # <= Cannot delete/clear this ns attr
                'xmlns:ns2'],
                [a.name for a in wrapped_elem.attribute_nodes])
        else:
            self.assertEqual(
                sorted(['a', 'ns2:d', 'ns2:x', 'xmlns:ns2']),
                sorted([a.name for a in wrapped_elem.attribute_nodes]))
        self.assertEqual('100', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns2:d'])
        self.assertEqual('urn:ns2', wrapped_elem.attributes['xmlns:ns2'])
        self.assertEqual('-5', wrapped_elem.attributes['ns2:x'])
        self.assertEqual('-5', wrapped_elem.attributes['{urn:ns2}x'])
        # Set/replace attributes via dict modification
        wrapped_elem.attributes['a'] = 200
        wrapped_elem.attributes['e'] = 'E'
        self.assertTrue(
            set(['a', 'e', 'ns2:d', 'ns2:x', 'xmlns:ns2']).issubset(
            set([a.name for a in wrapped_elem.attribute_nodes])))
        self.assertEqual('200', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns2:d'])
        self.assertEqual('E', wrapped_elem.attributes['e'])
        # In-place modifications to attribute reflected in element
        attr_dict = wrapped_elem.attributes
        attr_dict['a'] = 'A'  # Modify
        attr_dict['b'] = 'B'  # Add
        del(attr_dict['e'])  # Delete
        self.assertTrue(
            set(['a', 'b', 'ns2:d', 'ns2:x', 'xmlns:ns2']).issubset(
            set([a.name for a in wrapped_elem.attribute_nodes])))
        self.assertEqual('A', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns2:d'])
        self.assertEqual(None, wrapped_elem.attributes['e'])
        # Contains works on attribute dict
        self.assertTrue('a' in wrapped_elem.attributes)
        self.assertFalse('e' in wrapped_elem.attributes)

    def test_element_text(self):
        # Get text on element
        wrapped_node = self.adapter_class.wrap_node(self.elem1, self.doc)
        self.assertEqual('Some text', wrapped_node.text)
        # Set text on element
        wrapped_node.text = 'Different text'
        self.assertEqual('Different text', wrapped_node.text)
        # Unset text on element (removes any text children)
        wrapped_node.text = None
        self.assertEqual(None, wrapped_node.text)
        self.assertEqual([], wrapped_node.children)

    def test_element_value(self):
        # Get value on element
        wrapped_node = self.adapter_class.wrap_node(self.elem1, self.doc)
        self.assertEqual('Some text', wrapped_node.text)
        # Only Minidom library distinguishes between node's text & value
        if isinstance(self, TestMinidomNodes):
            self.assertIsNone(wrapped_node.value)
        else:
            self.assertEqual('Some text', wrapped_node.value)
        # Set value on element
        wrapped_node.value = 'Different text'
        self.assertEqual('Different text', wrapped_node.value)
        # Unset value on element
        wrapped_node.value = None
        self.assertEqual(None, wrapped_node.value)

    def test_delete(self):
        # Remove single Element using delete() method without destroying it
        self.assertEqual(
            [u'元素1', 'Element2', 'Element3', 'Element4'],
            [n.name for n in self.xml4h_root.children])
        removed_child = self.xml4h_root.children[0].delete(destroy=False)
        self.assertEqual(u'元素1', removed_child.name)
        self.assertEqual(
            ['Element2', 'Element3', 'Element4'],
            [n.name for n in self.xml4h_root.children])
        self.assertEqual(6, len(self.xml4h_root.find_doc()))
        # Remove Element using delete() and destroy it
        removed_child = self.xml4h_root.children.first.delete()
        self.assertIs(None, removed_child)
        self.assertEqual(
            ['Element3', 'Element4'],
            [n.name for n in self.xml4h_root.children])
        self.assertEqual(5, len(self.xml4h_root.find_doc()))

    def test_find_methods(self):
        # Find all elements in document
        elems = self.xml4h_root.find_doc()
        self.assertEqual(7, len(elems))
        elems = self.xml4h_root.document.find()
        self.assertEqual(7, len(elems))
        # Find all element descendants of root
        elems = self.xml4h_root.find()
        self.assertEqual(6, len(elems))
        # Find when no element names match
        elems = self.xml4h_root.find('NoMatchingName')
        self.assertEqual(0, len(elems))
        self.assertEqual([], elems)
        # Find non-namespaced element
        elems = self.xml4h_root.find(u'元素1')
        self.assertEqual(1, len(elems))
        self.assertIsInstance(elems[0], xml4h.nodes.Element)
        # Find multiple non-namespaced elements
        elems = self.xml4h_root.find('Element2')
        self.assertEqual(2, len(elems))
        self.assertIsInstance(elems[0], xml4h.nodes.Element)
        self.assertIsInstance(elems[1], xml4h.nodes.Element)
        self.assertEqual('DocRoot', elems[0].parent.name)
        self.assertEqual('Element3', elems[1].parent.name)
        # Find namespaced elements (only 1 Element3 in each namespace)
        elems = self.xml4h_root.find('Element3', ns_uri='urn:ns1')
        self.assertEqual(1, len(elems))
        self.assertEqual('DocRoot', elems[0].parent.name)
        elems = self.xml4h_root.find('Element3', ns_uri='urn:ns2')
        self.assertEqual(1, len(elems))
        self.assertEqual('Element4', elems[0].parent.name)
        # Non-namespaced find will find elements across namespaces
        elems = self.xml4h_root.find('Element3')
        self.assertEqual(2, len(elems))
        # Find only elements in a given namespace
        elems = self.xml4h_root.find(ns_uri='urn:ns1')
        self.assertEqual(2, len(elems))
        self.assertEqual('Element3', elems[0].name)
        self.assertEqual('DocRoot', elems[0].parent.name)
        self.assertEqual('Element4', elems[1].name)
        elems = self.xml4h_root.find(ns_uri='urn:ns2')
        self.assertEqual(1, len(elems))
        self.assertEqual('ns2:Element3', elems[0].name)
        self.assertEqual('Element3', elems[0].local_name)
        self.assertEqual('Element4', elems[0].parent.name)
        # Chain finds
        self.xml4h_root.find('Element3')[0].find
        # Find first only
        self.assertEqual(None, self.xml4h_root.find_first('NoMatchingName'))
        self.assertEqual(self.elem1,
                self.xml4h_root.find_first(u'元素1').impl_node)
        self.assertEqual(self.elem2,
                self.xml4h_root.find_first('Element2').impl_node)

    def test_has_feature(self):
        # Adapter and node has_feature tests must agree
        self.assertEqual(
            self.adapter_class.has_feature('xpath'),
            self.xml4h_root.has_feature('xpath'))
        # XPath is available in lxml adapter
        if self.adapter_class == xml4h.LXMLAdapter:
            self.assertTrue(self.adapter_class.has_feature('xpath'))
        # XPath is available in ElementTree adapter
        if self.adapter_class in (
                xml4h.ElementTreeAdapter, xml4h.cElementTreeAdapter):
            self.assertTrue(self.adapter_class.has_feature('xpath'))
        # XPath is not available in minidom adapter
        if self.adapter_class == xml4h.XmlDomImplAdapter:
            self.assertFalse(self.adapter_class.has_feature('xpath'))

    def test_xpath_feature_check(self):
        # Ensure appropriate exception thrown if XPath is not supported
        if not self.adapter_class.has_feature('xpath'):
            self.assertRaises(xml4h.exceptions.FeatureUnavailableException,
                self.xml4h_root.xpath, '/')

    def test_xpath_limited_support_queries(self):
        """
        Basic XPath queries as supported by (c)ElementTree version 1.3+
        """
        if not self.adapter_class.has_feature('xpath'):
            self.skipTest("XPath feature is not supported by %s"
                          % self.adapter_class)
        # Find current element
        self.assertEqual([self.xml4h_root], self.xml4h_root.xpath('.'))
        # Find child elements of root
        self.assertEqual(self.xml4h_root.children, self.xml4h_root.xpath('*'))
        # Find all elements in document
        elems = self.xml4h_doc.xpath('.//*')
        if self.adapter_class in (
                xml4h.ElementTreeAdapter, xml4h.cElementTreeAdapter):
            # TODO: (c)ElementTree incorrectly includes non-Element nodes
            self.assertEqual(8, len(elems))
        else:
            self.assertEqual(6, len(elems))
            self.assertEqual(self.xml4h_root.find(), elems)
        # Find when no element names match
        elems = self.xml4h_root.xpath('NoMatchingName')
        self.assertEqual([], elems)
        # Lookup parent of descendent node (fairly pointless...)
        self.assertEqual([self.xml4h_root],
            self.xml4h_root.xpath('Element2/..'))
        self.assertEqual([self.xml4h_root.Element4],
            self.xml4h_root.xpath('.//x:Element3/..',
                                  namespaces={'x': 'urn:ns2'}))
        # Lookup elements with a given attribute
        self.assertEqual(1, len(self.xml4h_root.xpath('.//*[@a]')))
        self.assertEqual(0, len(self.xml4h_root.xpath('.//*[@not-an-attr]')))
        # Lookup elements with a given attribute value
        self.assertEqual(1, len(self.xml4h_root.xpath(".//*[@a='1']")))
        self.assertEqual(0, len(self.xml4h_root.xpath(".//*[@a='wrong']")))
        # Find namespaced element with explicit namespaces definition
        self.assertEqual(self.elem3, self.xml4h_root.xpath(
            './/explicit:Element3', namespaces={'explicit': 'urn:ns1'})
                [0].impl_node)
        # Find namespaced element with helper empty/default prefix '_'
        self.assertEqual(self.elem3, self.xml4h_root.xpath(
            './/_:Element3', namespaces={None: 'urn:ns1'})
                [0].impl_node)

    def test_xpath(self):
        if not self.adapter_class.has_feature('xpath'):
            self.skipTest("XPath feature is not supported by %s"
                          % self.adapter_class)
        if self.adapter_class in (
                xml4h.ElementTreeAdapter, xml4h.cElementTreeAdapter):
            self.skipTest(
                "Only limited XPath support is available in (c)ElementTree"
                ", so most of these tests would fail for that implementation")
        # Find elements at root
        self.assertEqual([self.xml4h_root], self.xml4h_root.xpath('/*'))
        # Find all elements in document
        elems = self.xml4h_root.xpath('//*')
        self.assertEqual(self.xml4h_root.document.find(), elems)
        self.assertEqual(7, len(elems))
        # Find default namespaced element with helper empty/default prefix '_'
        self.assertEqual([self.xml4h_root],
            self.xml4h_root.xpath('/_:DocRoot'))
        # Start default namespaced query from Document
        self.assertEqual([self.xml4h_root],
            self.xml4h_doc.xpath('/_:DocRoot'))
        # Find all element descendants of root
        self.assertEqual(self.xml4h_root.find(),
            self.xml4h_root.xpath('/_:DocRoot//*'))
        # Find when no element names match
        elems = self.xml4h_root.xpath('//NoMatchingName')
        self.assertEqual([], elems)
        # Find non-namespaced element
        elems = self.xml4h_root.xpath(u'//元素1')
        self.assertEqual(self.xml4h_root.find(u'元素1'), elems)
        # Find multiple non-namespaced elements
        elems = self.xml4h_root.xpath('//Element2')
        self.assertEqual(
            [self.xml4h_root.Element2, self.xml4h_root.Element3.Element2],
            elems)
        # Find namespaced elements (only 1 Element3 in each namespace)
        # requires explicit namepsace mappings to work
        elems = self.xml4h_root.xpath('//ns1:Element3',
            namespaces={'ns1': 'urn:ns1'})
        self.assertEqual([self.xml4h_root.Element3], elems)
        # Find only elements with a given namespace
        elems = self.xml4h_root.xpath('//x:*', namespaces={'x': 'urn:ns1'})
        self.assertEqual(
            [self.xml4h_root.Element3, self.xml4h_root.Element4], elems)
        elems = self.xml4h_root.xpath('//x:*', namespaces={'x': 'urn:ns2'})
        self.assertEqual([self.xml4h_root.Element4.Element3], elems)
        # Find a node's parent
        elems = self.xml4h_root.xpath('//x:Element3/..',
            namespaces={'x': 'urn:ns2'})
        self.assertEqual([self.xml4h_root.Element4], elems)
        # Find just the first/last results
        elems = self.xml4h_root.xpath('//x:*[1]',
            namespaces={'x': 'urn:ns1'})
        self.assertEqual([self.xml4h_root.Element3], elems)
        elems = self.xml4h_root.xpath('//x:*[last()]',
            namespaces={'x': 'urn:ns1'})
        self.assertEqual([self.xml4h_root.Element4], elems)
        # Lookup attribute
        result = self.xml4h_root.xpath(u'//元素1/@a',
            namespaces={'x': 'urn:ns2'})
        self.assertEqual(['1'], result)
        # Lookup text
        result = self.xml4h_root.xpath(u'//元素1/text()',
            namespaces={'x': 'urn:ns2'})
        self.assertEqual(['Some text'], result)
        # sum() aggregate function
        result = self.xml4h_root.xpath(u'sum(//元素1/@*)',
            namespaces={'x': 'urn:ns2'})
        self.assertEqual(3, result)

    def test_magical_traversal(self):
        # Look up a non-existent child element by Python attribute
        try:
            self.xml4h_root.DoesNotExist
            self.fail('Expected AttributeError')
        except AttributeError as e:
            self.assertEqual(
                """<xml4h.nodes.Element: "DocRoot"> object"""
                """ has no attribute 'DoesNotExist'""",
                str(e))
        # Look up non-existent attribute by Python key name
        try:
            self.xml4h_root['not-an-attribute']
        except KeyError as e:
            self.assertEqual("'not-an-attribute'", str(e))

        # Look up child element by attribute
        self.assertEqual(self.xml4h_root, self.xml4h_doc.DocRoot)
        # Look up child element by attribute to depth
        self.assertEqual('A comment',
            self.xml4h_doc.DocRoot.Element3.Element2.children.first.value)
        # Look up a namespaced element; namespace prefix is not required
        self.assertEqual(self.elem3_second,
            self.xml4h_doc.DocRoot.Element4.Element3.impl_node)
        # Look up also works with trailing underscores
        self.assertEqual(self.elem3_second,
            self.xml4h_doc.DocRoot_.Element4_.Element3_.impl_node)

        # Add and look up a lowercase element name:
        self.xml4h_root.add_element('lowercasename', text='value')
        # Magical traversal works as normal...
        self.assertEqual('value', self.xml4h_root.lowercasename.text)
        # ...and also works with trailing underscores
        self.assertEqual('value', self.xml4h_root.lowercasename_.text)

        # Add and look up an element name that clashes with class attribute
        self.xml4h_root.add_element('child', text='value2')
        # Normal magical traversal finds class attribute, not child element
        self.assertEqual(types.MethodType, type(self.xml4h_root.child))
        # Trailing underscore allows for look up of child element
        self.assertEqual('value2', self.xml4h_root.child_.text)

        # Create and look up an illegal element name
        self.xml4h_root.add_element('_leadingunderscore', text='value2')
        self.assertEqual(
            'value2',
            self.xml4h_root.child('_leadingunderscore').text)
        try:
            self.xml4h_root._leadingunderscore
            self.fail('Expected AttributeError')
        except AttributeError as e:
            pass
        try:
            self.xml4h_root._leadingunderscore_
            self.fail('Expected AttributeError')
        except AttributeError as e:
            pass

        # Look up an attribute by key name
        self.assertEqual('2',
            self.xml4h_doc.DocRoot.child(u'元素1')['ns1:b'])


class TestMinidomNodes(BaseTestNodes, unittest.TestCase):

    @property
    def adapter_class(self):
        return xml4h.XmlDomImplAdapter

    def setUp(self):
        import xml.dom
        # Build a DOM using minidom for testing
        factory = xml.dom.getDOMImplementation('minidom')
        ns_uri = 'urn:test'
        doctype = None
        doc = factory.createDocument(ns_uri, 'DocRoot', doctype)
        self.root_elem = doc.firstChild
        self.elem1 = doc.createElement(u'元素1')
        self.elem1.setAttribute('a', '1')
        self.elem1.setAttributeNS('urn:ns1', 'ns1:b', '2')
        self.elem1.setAttributeNS(
            xml4h.nodes.Node.XMLNS_URI, 'xmlns:ns1', 'urn:ns1')
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
        self.xml4h_doc = xml4h.XmlDomImplAdapter.wrap_document(doc)
        self.xml4h_root = self.xml4h_doc.root
        self.xml4h_text = xml4h.XmlDomImplAdapter.wrap_node(
            self.text_node, self.doc)


class TestLXMLNodes(BaseTestNodes, unittest.TestCase):

    @property
    def adapter_class(self):
        return xml4h.LXMLAdapter

    def setUp(self):
        if not xml4h.LXMLAdapter.is_available():
            self.skipTest("lxml library is not installed")
        from lxml import etree
        # Build a DOM using minidom for testing
        self.root_elem = etree.Element('{urn:test}DocRoot', nsmap={
            None: 'urn:test'})
        doc = etree.ElementTree(self.root_elem)

        self.elem1 = etree.Element(u'元素1',
            nsmap={'ns1': 'urn:ns1'})
        self.elem1.attrib['a'] = '1'
        self.elem1.attrib['{urn:ns1}b'] = '2'
        self.elem2 = etree.Element('Element2')
        self.elem3 = etree.Element('{urn:ns1}Element3',
            nsmap={None: 'urn:ns1'})
        self.elem4 = etree.Element('{urn:ns1}Element4',
            nsmap={None: 'urn:ns1'})
        self.elem2_second = etree.Element('Element2')
        self.elem3_second = etree.Element('{urn:ns2}Element3',
            nsmap={'ns2': 'urn:ns2'})

        self.text_node = xml4h.impls.lxml_etree.LXMLText(
            'Some text', self.elem1)
        self.elem1.text = self.text_node.text
        self.cdata_node = xml4h.impls.lxml_etree.LXMLText(
            'Some cdata', self.elem2, is_cdata=True)
        self.elem2.text = self.cdata_node.text
        self.comment_node = etree.Comment('A comment')
        self.instruction_node = etree.ProcessingInstruction(
           'pi-target', 'pi-data')
        self.root_elem.append(self.elem1)
        self.root_elem.append(self.elem2)
        self.root_elem.append(self.elem3)
        self.root_elem.append(self.elem4)
        self.elem3.append(self.elem2_second)
        self.elem2_second.append(self.comment_node)
        self.elem4.append(self.elem3_second)
        self.elem3_second.append(self.instruction_node)

        self.doc = doc
        self.xml4h_doc = xml4h.LXMLAdapter.wrap_document(doc)
        self.xml4h_root = self.xml4h_doc.root
        self.xml4h_text = xml4h.LXMLAdapter.wrap_node(self.text_node, self.doc)


class TestElementTreeNodes(BaseTestNodes, unittest.TestCase):

    @property
    def adapter_class(self):
        return xml4h.ElementTreeAdapter

    def setUp(self):
        # Use c-based or pure python ElementTree impl based on test class
        if self.__class__ == TestcElementTreeNodes:
            if not self.adapter_class.is_available():
                self.skipTest(
                    "C-based ElementTree library is not installed"
                    " or is too outdated to be supported by xml4h")
            import xml.etree.cElementTree as ET
        else:
            if not self.adapter_class.is_available():
                self.skipTest(
                    "Pure Python ElementTree library is not installed"
                    " or is not too outdated to be supported by xml4h")
            import xml.etree.ElementTree as ET

        # Build a DOM using minidom for testing
        self.root_elem = ET.Element('{urn:test}DocRoot')
        doc = ET.ElementTree(self.root_elem)

        self.elem1 = ET.Element(u'元素1')
        self.elem1.attrib['xmlns:ns1'] = 'urn:ns1'
        self.elem1.attrib['a'] = '1'
        self.elem1.attrib['{urn:ns1}b'] = '2'
        self.elem2 = ET.Element('Element2')
        self.elem3 = ET.Element('{urn:ns1}Element3')
        self.elem3.attrib['xmlns'] = 'urn:ns1'
        self.elem4 = ET.Element('{urn:ns1}Element4')
        self.elem3.attrib['xmlns'] = 'urn:ns1'
        self.elem2_second = ET.Element('Element2')
        self.elem3_second = ET.Element('{urn:ns2}Element3')
        self.elem3_second.attrib['xmlns:ns2'] = 'urn:ns2'

        self.text_node = xml4h.impls.xml_etree_elementtree.ElementTreeText(
            'Some text', self.elem1)
        self.elem1.text = self.text_node.text
        self.cdata_node = xml4h.impls.xml_etree_elementtree.ElementTreeText(
            'Some cdata', self.elem2, is_cdata=True)
        self.elem2.text = self.cdata_node.text
        self.comment_node = ET.Comment('A comment')
        self.instruction_node = ET.ProcessingInstruction(
           'pi-target', 'pi-data')
        self.root_elem.append(self.elem1)
        self.root_elem.append(self.elem2)
        self.root_elem.append(self.elem3)
        self.root_elem.append(self.elem4)
        self.elem3.append(self.elem2_second)
        self.elem2_second.append(self.comment_node)
        self.elem4.append(self.elem3_second)
        self.elem3_second.append(self.instruction_node)

        self.doc = doc
        self.xml4h_doc = self.adapter_class.wrap_document(doc)
        self.xml4h_root = self.xml4h_doc.root
        self.xml4h_text = self.adapter_class.wrap_node(
            self.text_node, self.doc)

    def test_ancestry_dict_cache(self):
        # Trigger creation and caching of ancestry dict
        xml4h_elem3_second = self.adapter_class.wrap_node(
            self.elem3_second, self.doc)
        self.assertEqual(self.elem4, xml4h_elem3_second.parent.impl_node)
        # Ancestry dict should now be primed
        self.assertEqual(self.elem4,
            xml4h_elem3_second.adapter.CACHED_ANCESTRY_DICT[self.elem3_second])
        # Confirm we can clear the cached ancestry dict
        xml4h_elem3_second.adapter.clear_caches()
        self.assertFalse(self.elem3_second in
            xml4h_elem3_second.adapter.CACHED_ANCESTRY_DICT)


# Note this class extends TestElementTreeNodes class, which performs tests
# against ElementTree/cElementTree implementations depending on name of class.
class TestcElementTreeNodes(TestElementTreeNodes, unittest.TestCase):

    @property
    def adapter_class(self):
        return xml4h.cElementTreeAdapter
