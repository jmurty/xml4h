from xml4h.impls.interface import _XmlImplWrapper
from xml4h.nodes import (Node, ElementNode, AttributeNode, TextNode,
    CDATANode, EntityNode, CommentNode, ProcessingInstructionNode)

import xml.dom


class XmlDomImplWrapper(_XmlImplWrapper):

    def create_doc_and_root_elem(cls, root_tagname,
            namespace_uri=None, impl_name=None, impl_features=None):
        # Create DOM implementation factory
        if impl_features is None:
            impl_features = []
        factory = xml.dom.getDOMImplementation(impl_name, impl_features)
        # Create Document from factory
        doctype = None  # TODO
        doc = factory.createDocument(
            namespace_uri, root_tagname, doctype)
        return doc, doc.firstChild

    def wrap_impl_node(self, impl_node, impl_document, impl_wrapper):
        if isinstance(impl_node, tuple):
            return AttributeNode(impl_node, impl_document, impl_wrapper)
        try:
            impl_class = {
                xml.dom.Node.ELEMENT_NODE: ElementNode,
                xml.dom.Node.ATTRIBUTE_NODE: AttributeNode,
                xml.dom.Node.TEXT_NODE: TextNode,
                xml.dom.Node.CDATA_SECTION_NODE: CDATANode,
                xml.dom.Node.ENTITY_NODE: EntityNode,
                xml.dom.Node.PROCESSING_INSTRUCTION_NODE:
                    ProcessingInstructionNode,
                xml.dom.Node.COMMENT_NODE: CommentNode,
                # TODO
                #xml.dom.Node.DOCUMENT_NODE: ,
                #xml.dom.Node.DOCUMENT_TYPE_NODE: ,
                #xml.dom.Node.NOTATION_NODE: ,
                }[impl_node.nodeType]
            return impl_class(impl_node, impl_document, impl_wrapper)
        except KeyError, e:
            raise NotImplementedError(
                'Wrapping of %s implementation nodes is not implemented'
                % impl_node)

    def map_node_type(self, node):
        try:
            return {
                xml.dom.Node.ELEMENT_NODE: Node.ELEMENT_NODE,
                xml.dom.Node.ATTRIBUTE_NODE: Node.ATTRIBUTE_NODE,
                xml.dom.Node.TEXT_NODE: Node.TEXT_NODE,
                xml.dom.Node.CDATA_SECTION_NODE: Node.CDATA_SECTION_NODE,
                xml.dom.Node.ENTITY_NODE: Node.ENTITY_NODE,
                xml.dom.Node.PROCESSING_INSTRUCTION_NODE:
                    Node.PROCESSING_INSTRUCTION_NODE,
                xml.dom.Node.COMMENT_NODE: Node.COMMENT_NODE,
                xml.dom.Node.DOCUMENT_NODE: Node.DOCUMENT_NODE,
                xml.dom.Node.DOCUMENT_TYPE_NODE: Node.DOCUMENT_TYPE_NODE,
                xml.dom.Node.NOTATION_NODE: Node.NOTATION_NODE,
                }[node.nodeType]
        except KeyError, e:
            raise Exception('Unknown implementation node type: %s'
                % node.nodeType)

    def get_root_element(self):
        return self.impl_document.firstChild

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

    def get_node_parent(self, element):
        return element.parentNode

    def get_node_children(self, element, namespace_uri=None):
        return element.childNodes

    def get_node_name(self, node):
        # Attribute "node" is actually a tuple
        if isinstance(node, tuple):
            return node[0]
        else:
            return node.nodeName

    def get_node_value(self, node):
        # Attribute "node" is actually a tuple
        if isinstance(node, tuple):
            return node[1]
        else:
            return node.nodeValue

    def get_node_attributes(self, element, namespace_uri=None):
        return element.attributes.items()

    def set_node_attribute(self, element, name, value, namespace_uri=None):
        if namespace_uri is not None:
            element.setAttributeNS(namespace_uri, name, value)
        else:
            element.setAttribute(name, value)

    def add_node_child(self, parent, child, before_sibling=None):
        if before_sibling is not None:
            parent.insertBefore(child, before_sibling)
        else:
            parent.appendChild(child)
