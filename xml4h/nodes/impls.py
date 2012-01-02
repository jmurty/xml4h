from xml4h.nodes import (Document, Node, ValueNode, NameValueNode,
    ElementNode, AttributeNode, ProcessingInstructionNode)

import xml


class XmlDomDocument(Document):

    def new_impl_element(self, tagname, namespace_uri=None):
        if namespace_uri is None:
            return self.impl_document.createElement(tagname)
        else:
            return self.impl_document.createElementNS(namespace_uri, tagname)

    def new_impl_text(self, text):
        return self.impl_document.createTextNode(text)

    def new_impl_comment(self, text):
        return self.impl_document.createComment(text)

    def new_impl_instruction(self, target, data):
        return self.impl_document.createProcessingInstruction(target, data)

    def new_impl_cdata(self, text):
        return self.impl_document.createCDATASection(text)


class XmlDomNode(Node):

    @classmethod
    def _wrap_impl_node(self, impl_node, impl_document):
        if isinstance(impl_node, tuple):
            return XmlDomAttributeNode(impl_node, impl_document)
        try:
            impl_class = {
                xml.dom.Node.ELEMENT_NODE: XmlDomElementNode,
                xml.dom.Node.ATTRIBUTE_NODE: XmlDomAttributeNode,
                xml.dom.Node.TEXT_NODE: XmlDomTextNode,
                xml.dom.Node.CDATA_SECTION_NODE: XmlDomCDATANode,
                xml.dom.Node.ENTITY_NODE: XmlDomEntityNode,
                xml.dom.Node.PROCESSING_INSTRUCTION_NODE:
                    XmlDomProcessingInstructionNode,
                xml.dom.Node.COMMENT_NODE: XmlDomCommentNode,
                }[impl_node.nodeType]
            return impl_class(impl_node, impl_document)
        except KeyError, e:
            raise NotImplementedError(
                'Wrapping of %s implementation nodes is not implemented'
                % impl_node)

    @classmethod
    def _wrap_impl_document(self, impl_document):
        return XmlDomDocument(impl_document)

    def _map_node_type(self, node):
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

    def _get_parent(self, element):
        return element.parentNode

    def _get_children(self, element, namespace_uri=None):
        return element.childNodes

    def _get_root_element(self):
        return self.impl_document.firstChild


class XmlDomValueNode(XmlDomNode, ValueNode):

    def _get_value(self, node):
        return node.nodeValue


class XmlDomNameValueNode(XmlDomValueNode, NameValueNode):

    def _get_name(self, node):
        return node.nodeName


class XmlDomAttributeNode(XmlDomNode, AttributeNode):

    def _get_name(self, node):
        return node[0]

    def _get_value(self, node):
        return node[1]


class XmlDomTextNode(XmlDomValueNode):
    pass

class XmlDomCDATANode(XmlDomValueNode):
    pass

class XmlDomEntityNode(XmlDomValueNode):
    pass

class XmlDomCommentNode(XmlDomValueNode):
    pass

class XmlDomProcessingInstructionNode(XmlDomNameValueNode,
        ProcessingInstructionNode):
    pass


class XmlDomElementNode(XmlDomNameValueNode, ElementNode):
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

    def _get_attributes(self, element, namespace_uri=None):
        return element.attributes.items()

    def __eq__(self, other):
        if super(XmlDomElementNode, self).__eq__(other):
            return True
        # xml.dom.Document's == test doesn't match equivalent docs
        # TODO Very inefficient
        return unicode(self) == unicode(other)
