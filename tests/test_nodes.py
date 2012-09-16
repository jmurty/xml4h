import unittest

from xml4h import nodes, exceptions
from xml4h.impls.xml_dom_minidom import XmlDomImplAdapter
from xml4h.impls.lxml_etree import LXMLAdapter, LXMLText


class BaseTestNodes(object):

    def test_wrap_document(self):
        wrapped_elem = self.my_adapter.wrap_node(self.root_elem, self.doc)
        self.assertEqual(self.root_elem, wrapped_elem.impl_node)
        self.assertEqual('DocRoot', wrapped_elem.name)
        self.assertEqual(self.doc, wrapped_elem.impl_document)

    def test_wrap_node_and_is_type_methods(self):
        # Wrap root element
        wrapped_node = self.my_adapter.wrap_node(self.root_elem, self.doc)
        self.assertEqual(self.root_elem, wrapped_node.impl_node)
        self.assertEqual('DocRoot', wrapped_node.name)
        self.assertEqual(self.doc, wrapped_node.impl_document)
        self.assertTrue(wrapped_node.is_type(nodes.ELEMENT_NODE))
        self.assertTrue(wrapped_node.is_element)
        # Wrap a non-root element
        wrapped_node = self.my_adapter.wrap_node(self.elem3_second, self.doc)
        self.assertEqual(self.elem3_second, wrapped_node.impl_node)
        self.assertEqual('ns2:Element3', wrapped_node.name)
        self.assertEqual('Element4', wrapped_node.parent.name)
        self.assertTrue(wrapped_node.is_type(nodes.ELEMENT_NODE))
        self.assertTrue(wrapped_node.is_element)
        # Test node types
        wrapped_node = self.my_adapter.wrap_node(self.text_node, self.doc)
        self.assertIsInstance(wrapped_node, nodes.Text)
        self.assertTrue(wrapped_node.is_type(nodes.TEXT_NODE))
        self.assertTrue(wrapped_node.is_text)
        wrapped_node = self.my_adapter.wrap_node(self.cdata_node, self.doc)
        self.assertIsInstance(wrapped_node, nodes.CDATA)
        self.assertTrue(wrapped_node.is_type(nodes.CDATA_NODE))
        self.assertTrue(wrapped_node.is_cdata)
        wrapped_node = self.my_adapter.wrap_node(self.comment_node, self.doc)
        self.assertIsInstance(wrapped_node, nodes.Comment)
        self.assertTrue(wrapped_node.is_type(nodes.COMMENT_NODE))
        self.assertTrue(wrapped_node.is_comment)
        wrapped_node = self.my_adapter.wrap_node(self.instruction_node, self.doc)
        self.assertIsInstance(wrapped_node, nodes.ProcessingInstruction)
        self.assertTrue(wrapped_node.is_type(nodes.PROCESSING_INSTRUCTION_NODE))
        self.assertTrue(wrapped_node.is_processing_instruction)

    def test_parent(self):
        # Document node has no parent
        wrapped_doc = self.my_adapter.wrap_node(self.doc, self.doc)
        self.assertEqual(None, wrapped_doc.parent)
        # Root element has document as parent
        self.assertIsInstance(self.wrapped_root.parent, nodes.Document)
        # Find parents of elements
        self.assertEqual(self.root_elem,
            self.my_adapter.wrap_node(self.elem1, self.doc).parent.impl_node)
        self.assertEqual(self.elem3,
            self.my_adapter.wrap_node(self.elem2_second, self.doc).parent.impl_node)
        # Parent of text node (Text not stored as node in lxml)
        if not isinstance(self, TestLXMLNodes):
            self.assertEqual(self.elem1,
                self.my_adapter.wrap_node(self.text_node, self.doc).parent.impl_node)
        # Chain parent calls
        wrapped_elem = self.my_adapter.wrap_node(self.elem3_second, self.doc)
        self.assertEqual(self.root_elem, wrapped_elem.parent.parent.impl_node)

    def test_ancestors(self):
        # Document node has no ancestors
        wrapped_doc = self.my_adapter.wrap_node(self.doc, self.doc)
        self.assertEqual([], wrapped_doc.ancestors)
        # Find ancestors of elements
        self.assertEqual(['DocRoot'],
            [a.name for a in
             self.my_adapter.wrap_node(self.elem1, self.doc).ancestors
             if a.is_element])
        self.assertEqual(['Element4', 'DocRoot'],
            [a.name for a in
             self.my_adapter.wrap_node(self.elem3_second, self.doc).ancestors
             if a.is_element])
        # Document root node (not Element) is included in ancestors list
        self.assertTrue(
            self.my_adapter.wrap_node(self.elem3_second, self.doc).ancestors[-1].is_document)

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
        wrapped_elem = self.my_adapter.wrap_node(self.elem1, self.doc)
        self.assertEqual(None, wrapped_elem.namespace_uri)
        self.assertEqual('Element1', wrapped_elem.name)
        self.assertEqual(None, wrapped_elem.prefix)
        self.assertEqual('Element1', wrapped_elem.local_name)
        # Namespace data for ns element without prefix
        wrapped_elem = self.my_adapter.wrap_node(self.elem3, self.doc)
        self.assertEqual('urn:ns1', wrapped_elem.namespace_uri)
        self.assertEqual('Element3', wrapped_elem.name)
        self.assertEqual(None, wrapped_elem.prefix)
        self.assertEqual('Element3', wrapped_elem.local_name)
        # Namespace data for ns element with prefix
        wrapped_elem = self.my_adapter.wrap_node(self.elem3_second, self.doc)
        self.assertEqual('urn:ns2', wrapped_elem.namespace_uri)
        self.assertEqual('ns2:Element3', wrapped_elem.name)
        self.assertEqual('ns2', wrapped_elem.prefix)
        self.assertEqual('Element3', wrapped_elem.local_name)
        # Namespace data for attribute node without namespace
        wrapped_elem = self.my_adapter.wrap_node(self.elem1, self.doc)
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
        wrapped_elem = self.my_adapter.wrap_node(self.elem1, self.doc)
        self.assertEqual(None, wrapped_elem.attributes.namespace_uri('a'))
        # Namespace data for attribute dict with namespace
        wrapped_elem = self.my_adapter.wrap_node(self.elem1, self.doc)
        self.assertEqual('urn:ns1', wrapped_elem.attributes.namespace_uri('ns1:b'))

    def test_name(self):
        wrapped_node = self.my_adapter.wrap_node(self.elem1, self.doc)
        self.assertEqual('Element1', wrapped_node.name)
        attribute_node = wrapped_node.attribute_nodes[0]
        self.assertEqual('a', attribute_node.name)
        wrapped_node = self.my_adapter.wrap_node(self.text_node, self.doc)
        self.assertEqual('#text', wrapped_node.name)
        wrapped_node = self.my_adapter.wrap_node(self.cdata_node, self.doc)
        self.assertEqual('#cdata-section', wrapped_node.name)
        wrapped_node =self.my_adapter.wrap_node(self.comment_node, self.doc)
        self.assertEqual('#comment', wrapped_node.name)
        wrapped_node = self.my_adapter.wrap_node(self.instruction_node, self.doc)
        self.assertEqual(wrapped_node.target, wrapped_node.name)

    def test_attributes(self):
        # Non-element nodes don't have attributes
        self.assertEqual(None, self.wrapped_doc.attributes)
        self.assertEqual(None, self.wrapped_doc.attribute_nodes)
        self.assertEqual(None, self.wrapped_text.attributes)
        self.assertEqual(None, self.wrapped_text.attribute_nodes)
        # Get element's attribute nodes
        wrapped_elem = self.my_adapter.wrap_node(self.elem1, self.doc)
        attr_nodes = wrapped_elem.attribute_nodes
        self.assertEqual(
            ['a', 'ns1:b', 'xmlns:ns1'],
            [a.name for a in attr_nodes])
        self.assertEqual(['1', '2', 'urn:ns1'], [a.value for a in attr_nodes])
        self.assertEqual(['a', 'b', 'ns1'], [a.local_name for a in attr_nodes])
        self.assertEqual([None, 'ns1', 'xmlns'], [a.prefix for a in attr_nodes])
        self.assertEqual(
            [None, 'urn:ns1', 'http://www.w3.org/2000/xmlns/'],
            [a.ns_uri for a in attr_nodes])
        # Get element's attributes dict
        wrapped_elem = self.my_adapter.wrap_node(self.elem1, self.doc)
        attrs_dict = wrapped_elem.attributes
        self.assertEqual(['a', 'ns1:b', 'xmlns:ns1'], attrs_dict.keys())
        self.assertEqual(['1', '2', 'urn:ns1'], attrs_dict.values())
        # Set/change attributes via element methods
        wrapped_elem.set_attributes({'a': 10, 'c': 3})
        self.assertEqual(['10', '3', '2', 'urn:ns1'],
            [a.value for a in wrapped_elem.attribute_nodes])
        # Set attributes via dict assignment (pre-existing attributes are deleted)
        wrapped_elem.attributes = {
            'a': 100,  # effectively replaces prior 'a' attribute
            'xmlns:ns1': 'urn:ns1',  # namespace definition
            'ns1:d': -3,  # attribute with namespace prefix
            '{urn:ns1}x': -5  # attribute with etree-style namespace URI
            }
        self.assertEqual(['a', 'ns1:d', 'ns1:x', 'xmlns:ns1'],
            [a.name for a in wrapped_elem.attribute_nodes])
        self.assertEqual('100', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns1:d'])
        self.assertEqual('urn:ns1', wrapped_elem.attributes['xmlns:ns1'])
        self.assertEqual('-5', wrapped_elem.attributes['ns1:x'])
        self.assertEqual('-5', wrapped_elem.attributes['{urn:ns1}x'])
        # Set/replace attributes via dict modification
        wrapped_elem.attributes['a'] = 200
        wrapped_elem.attributes['e'] = 'E'
        self.assertEqual(['a', 'e', 'ns1:d', 'ns1:x', 'xmlns:ns1'],
            [a.name for a in wrapped_elem.attribute_nodes])
        self.assertEqual('200', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns1:d'])
        self.assertEqual('E', wrapped_elem.attributes['e'])
        # In-place modifications to attribute reflected in element
        attr_dict = wrapped_elem.attributes
        attr_dict['a'] = 'A' # Modify
        attr_dict['b'] = 'B' # Add
        del(attr_dict['e']) # Delete
        self.assertEqual(['a', 'b', 'ns1:d', 'ns1:x', 'xmlns:ns1'],
            [a.name for a in wrapped_elem.attribute_nodes])
        self.assertEqual('A', wrapped_elem.attributes['a'])
        self.assertEqual('-3', wrapped_elem.attributes['ns1:d'])
        self.assertEqual(None, wrapped_elem.attributes['e'])
        # Contains works on attribute dict
        self.assertTrue('a' in wrapped_elem.attributes)
        self.assertFalse('e' in wrapped_elem.attributes)

    def test_element_text(self):
        # Get text on element
        wrapped_node = self.my_adapter.wrap_node(self.elem1, self.doc)
        self.assertEqual('Some text', wrapped_node.text)
        # Set text on element
        wrapped_node.text = 'Different text'
        self.assertEqual('Different text', wrapped_node.text)
        self.assertEqual(
            wrapped_node.children[0].value,
            self.my_adapter(self.doc).get_node_value(
                wrapped_node.children[0].impl_node))
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
        elems = self.wrapped_root.doc_find()
        self.assertEqual(7, len(elems))
        elems = self.wrapped_root.document.find()
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

    def test_xpath(self):
        # Ensure appropriate exception thrown if XPath is not supported
        if not self.my_adapter.has_feature('xpath'):
            self.assertRaises(exceptions.FeatureUnavailableException,
                self.wrapped_root.xpath, '/')
            self.skipTest("XPath feature is not supported by %s"
                          % self.my_adapter)
        # Find elements at root
        self.assertEqual([self.wrapped_root], self.wrapped_root.xpath('/*'))
        # Find all elements in document
        elems = self.wrapped_root.xpath('//*')
        self.assertEqual(7, len(elems))
        self.assertEqual(self.wrapped_root.document.find(), elems)
        # Find default namespaced element with helper empty/default prefix '_'
        self.assertEqual([self.wrapped_root],
            self.wrapped_root.xpath('/_:DocRoot'))
        # Find all element descendants of root
        self.assertEqual(self.wrapped_root.find(),
            self.wrapped_root.xpath('/_:DocRoot//*'))
        # Find when no element names match
        elems = self.wrapped_root.xpath('//NoMatchingName')
        self.assertEqual([], elems)
        # Find non-namespaced element
        elems = self.wrapped_root.xpath('//Element1')
        self.assertEqual(self.wrapped_root.find('Element1'), elems)
        # Find multiple non-namespaced elements
        elems = self.wrapped_root.xpath('//Element2')
        self.assertEqual(
            [self.wrapped_root.Element2, self.wrapped_root.Element3.Element2],
            elems)
        # Find namespaced elements (only 1 Element3 in each namespace)
        # requires explicit namepsace mappings to work
        elems = self.wrapped_root.xpath('//ns1:Element3',
            namespaces={'ns1': 'urn:ns1'})
        self.assertEqual([self.wrapped_root.Element3], elems)
        # Find only elements with a given namespace
        elems = self.wrapped_root.xpath('//x:*', namespaces={'x': 'urn:ns1'})
        self.assertEqual(
            [self.wrapped_root.Element3, self.wrapped_root.Element4], elems)
        elems = self.wrapped_root.xpath('//x:*', namespaces={'x': 'urn:ns2'})
        self.assertEqual([self.wrapped_root.Element4.Element3], elems)
        # Find a node's parent
        elems = self.wrapped_root.xpath('//x:Element3/..',
            namespaces={'x': 'urn:ns2'})
        self.assertEqual([self.wrapped_root.Element4], elems)
        # Find just the first/last results
        elems = self.wrapped_root.xpath('//x:*[1]',
            namespaces={'x': 'urn:ns1'})
        self.assertEqual([self.wrapped_root.Element3], elems)
        elems = self.wrapped_root.xpath('//x:*[last()]',
            namespaces={'x': 'urn:ns1'})
        self.assertEqual([self.wrapped_root.Element4], elems)
        # Lookup attribute
        result = self.wrapped_root.xpath('//Element1/@a',
            namespaces={'x': 'urn:ns2'})
        self.assertEqual(['1'], result)
        # Lookup text
        result = self.wrapped_root.xpath('//Element1/text()',
            namespaces={'x': 'urn:ns2'})
        self.assertEqual(['Some text'], result)
        # sum() aggregate function
        result = self.wrapped_root.xpath('sum(//Element1/@*)',
            namespaces={'x': 'urn:ns2'})
        self.assertEqual(3, result)


class TestMinidomNodes(BaseTestNodes, unittest.TestCase):

    @property
    def my_adapter(self):
        return XmlDomImplAdapter

    def setUp(self):
        import xml.dom
        # Build a DOM using minidom for testing
        factory = xml.dom.getDOMImplementation('minidom')
        ns_uri = 'urn:test'
        doctype = None
        doc = factory.createDocument(ns_uri, 'DocRoot', doctype)
        self.root_elem = doc.firstChild
        self.elem1 = doc.createElement('Element1')
        self.elem1.setAttribute('a', '1')
        self.elem1.setAttributeNS('urn:ns1', 'ns1:b', '2')
        self.elem1.setAttributeNS(nodes.Node.XMLNS_URI, 'xmlns:ns1', 'urn:ns1')
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
        self.wrapped_doc = XmlDomImplAdapter.wrap_document(doc)
        self.wrapped_root = self.wrapped_doc.root
        self.wrapped_text = XmlDomImplAdapter.wrap_node(self.text_node, self.doc)


class TestLXMLNodes(BaseTestNodes, unittest.TestCase):

    @property
    def my_adapter(self):
        return LXMLAdapter

    def setUp(self):
        if not LXMLAdapter.is_available():
            self.skipTest("lxml library is not installed")
        from lxml import etree
        # Build a DOM using minidom for testing
        self.root_elem = etree.Element('{urn:test}DocRoot', nsmap={
            None: 'urn:test'})
        doc = etree.ElementTree(self.root_elem)

        self.elem1 = etree.Element('Element1', nsmap={
            'ns1': 'urn:ns1'})
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

        self.text_node = LXMLText('Some text', self.elem1)
        self.elem1.text = self.text_node.text
        self.cdata_node = LXMLText('Some cdata', self.elem2, is_cdata=True)
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
        self.wrapped_doc = LXMLAdapter.wrap_document(doc)
        self.wrapped_root = self.wrapped_doc.root
        self.wrapped_text = LXMLAdapter.wrap_node(self.text_node, self.doc)

