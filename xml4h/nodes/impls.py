import re
from StringIO import StringIO

import xml

from xml4h import is_pyxml_installed
from xml4h.nodes import (Node, ValueNode, NameValueNode,
    ElementNode, AttributeNode, ProcessingInstructionNode)


class XmlDomNode(Node):

    @classmethod
    def _build_wrap_node(self, impl_node, impl_document):
        if not isinstance(impl_document, xml.dom.minidom.Document):
            raise Exception('oops')
        if isinstance(impl_node, tuple):
            return XmlDomAttributeNode(impl_node, impl_document)
        elif impl_node.nodeType == xml.dom.Node.ELEMENT_NODE:
            return XmlDomElementNode(impl_node, impl_document)
        elif (impl_node.nodeType == xml.dom.Node.TEXT_NODE
                or impl_node.nodeType == xml.dom.Node.COMMENT_NODE):
            return XmlDomValueNode(impl_node, impl_document)
        elif impl_node.nodeType == xml.dom.Node.PROCESSING_INSTRUCTION_NODE:
            return XmlDomProcessingInstructionNode(impl_node, impl_document)
        raise NotImplementedError(
            'Wrapping of %s implementation nodes is not implemented'
            % impl_node)

    def _get_node_type(self, node):
        try:
            return {
                xml.dom.Node.ELEMENT_NODE: Node.ELEMENT_NODE,
                xml.dom.Node.ATTRIBUTE_NODE: Node.ATTRIBUTE_NODE,
                xml.dom.Node.TEXT_NODE: Node.TEXT_NODE,
                xml.dom.Node.CDATA_SECTION_NODE: Node.CDATA_SECTION_NODE,
                xml.dom.Node.ENTITY_NODE: Node.ENTITY_NODE,
                xml.dom.Node.PROCESSING_INSTRUCTION_NODE: Node.PROCESSING_INSTRUCTION_NODE,
                xml.dom.Node.COMMENT_NODE: Node.COMMENT_NODE,
                xml.dom.Node.DOCUMENT_NODE: Node.DOCUMENT_NODE,
                xml.dom.Node.DOCUMENT_TYPE_NODE: Node.DOCUMENT_TYPE_NODE,
                xml.dom.Node.NOTATION_NODE: Node.NOTATION_NODE,
                }[node.nodeType]
        except KeyError, e:
            raise Exception('Unknown implementation node type: %s'
                % node.nodeType)

    def _new_element_node(self, tagname, namespace_uri=None):
        if namespace_uri is None:
            return self.impl_document.createElement(tagname)
        else:
            return self.impl_document.createElementNS(namespace_uri, tagname)

    def _new_text_node(self, text):
        return self.impl_document.createTextNode(text)

    def _new_comment_node(self, text):
        return self.impl_document.createComment(text)

    def _new_processing_instruction_node(self, target, data):
        return self.impl_document.createProcessingInstruction(target, data)

    def _get_parent(self, element):
        return element.parentNode

    def _get_children(self, element, namespace_uri=None):
        return element.childNodes

    def _get_root_element(self):
        return self.impl_document.firstChild


class XmlDomValueNode(XmlDomNode, ValueNode):

    def _get_value(self, node):
        return node.nodeValue


class XmlDomAttributeNode(XmlDomNode, AttributeNode):

    def _get_name(self, node):
        return node[0]

    def _get_value(self, node):
        return node[1]


class XmlDomProcessingInstructionNode(XmlDomNode, ProcessingInstructionNode):

    def _get_name(self, node):
        return node.nodeName

    def _get_value(self, node):
        return node.nodeValue


class XmlDomElementNode(XmlDomNode, ElementNode):
    '''
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.

    This class wraps the xml.dom module included with Python 2.0+
    '''

    @classmethod
    def create(cls, dom_impl, root_tagname, namespace_uri=None):
        doctype = None  # TODO
        doc = dom_impl.createDocument(
            namespace_uri, root_tagname, doctype)
        builder = cls(doc.firstChild, doc)
        # Automatically add namespace URI to root Element as attribute
        if namespace_uri is not None:
            builder._set_attribute(doc.firstChild, 'xmlns', namespace_uri,
                namespace_uri='http://www.w3.org/2000/xmlns/')
        return builder

    def _add_child_node(self, parent, child, before_sibling=None):
        if before_sibling is not None:
            parent.insertBefore(child, before_sibling)
        else:
            parent.appendChild(child)

    def _set_attribute(self, element, name, value, namespace_uri=None):
        if namespace_uri is not None:
            element.setAttributeNS(namespace_uri, name, value)
        else:
            element.setAttribute(name, value)

    def _get_attributes(self, namespace_uri=None):
        return self.impl_node.attributes.items()

    @property
    def _attribute_class(self):
        return XmlDomAttributeNode

    def _get_tagname(self, element):
        return element.nodeName

    def __eq__(self, other):
        if super(XmlDomElementNode, self).__eq__(other):
            return True
        # xml.dom.Document's == test doesn't match equivalent docs
        return unicode(self) == unicode(other)

    def _get_name(self, node):
        return node.tagName

    def _get_value(self, node):
        return node.value
