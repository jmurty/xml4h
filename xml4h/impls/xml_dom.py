from xml4h.impls.interface import _XmlImplAdapter
from xml4h import nodes

import xml.dom


class XmlDomImplAdapter(_XmlImplAdapter):

    @classmethod
    def new_impl_document(self, root_tagname, ns_uri=None,
            impl_name=None, impl_features=None):
        # Create DOM implementation factory
        if impl_features is None:
            impl_features = []
        factory = xml.dom.getDOMImplementation(impl_name, impl_features)
        # Create Document from factory
        doctype = None  # TODO
        doc = factory.createDocument(ns_uri, root_tagname, doctype)
        return doc

    def map_node_to_class(self, impl_node):
        try:
            return {
                xml.dom.Node.ELEMENT_NODE: nodes.Element,
                xml.dom.Node.ATTRIBUTE_NODE: nodes.Attribute,
                xml.dom.Node.TEXT_NODE: nodes.Text,
                xml.dom.Node.CDATA_SECTION_NODE: nodes.CDATA,
                # EntityReference not supported by minidom
                #xml.dom.Node.ENTITY_REFERENCE: nodes.EntityReference,
                xml.dom.Node.ENTITY_NODE: nodes.Entity,
                xml.dom.Node.PROCESSING_INSTRUCTION_NODE:
                    nodes.ProcessingInstruction,
                xml.dom.Node.COMMENT_NODE: nodes.Comment,
                xml.dom.Node.DOCUMENT_NODE: nodes.Document,
                xml.dom.Node.DOCUMENT_TYPE_NODE: nodes.DocumentType,
                xml.dom.Node.DOCUMENT_FRAGMENT_NODE: nodes.DocumentFragment,
                xml.dom.Node.NOTATION_NODE: nodes.Notation,
                }[impl_node.nodeType]
        except KeyError, e:
            raise Exception(
                'Unrecognized type for implementation node: %s' % impl_node)

    def new_impl_element(self, tagname, ns_uri=None):
        return self.impl_document.createElementNS(ns_uri, tagname)

    def new_impl_text(self, text):
        return self.impl_document.createTextNode(text)

    def new_impl_comment(self, text):
        return self.impl_document.createComment(text)

    def new_impl_instruction(self, target, data):
        return self.impl_document.createProcessingInstruction(target, data)

    def new_impl_cdata(self, text):
        return self.impl_document.createCDATASection(text)

    def find_node_elements(self, node, name='*', ns_uri='*'):
        return node.getElementsByTagNameNS(ns_uri, name)

    def get_node_namespace_uri(self, node):
        return node.namespaceURI

    def set_node_namespace_uri(self, node, ns_uri):
        node.namespaceURI = ns_uri

    def get_node_parent(self, element):
        return element.parentNode

    def get_node_children(self, element):
        return element.childNodes

    def get_node_name(self, node):
        return node.nodeName

    def get_node_value(self, node):
        return node.nodeValue

    def get_node_attributes(self, element, ns_uri=None):
        attr_nodes = []
        for attr_name in element.attributes.keys():
            if self.has_node_attribute(element, attr_name, ns_uri):
                attr_nodes.append(
                    self.get_node_attribute_node(element, attr_name, ns_uri))
        return attr_nodes

    def has_node_attribute(self, element, name, ns_uri=None):
        if ns_uri is not None:
            return element.hasAttributeNS(ns_uri, name)
        else:
            return element.hasAttribute(name)

    def get_node_attribute_node(self, element, name, ns_uri=None):
        if ns_uri is not None:
            return element.getAttributeNodeNS(ns_uri, name)
        else:
            return element.getAttributeNode(name)

    def get_node_attribute_value(self, element, name, ns_uri=None):
        if ns_uri is not None:
            return element.getAttributeNS(ns_uri, name)
        else:
            return element.getAttribute(name)

    def set_node_attribute_value(self, element, name, value, ns_uri=None):
        element.setAttributeNS(ns_uri, name, value)

    def remove_node_attribute(self, element, name, ns_uri=None):
        if ns_uri is not None:
            element.removeAttributeNS(ns_uri, name)
        else:
            element.removeAttribute(name)

    def add_node_child(self, parent, child, before_sibling=None):
        if before_sibling is not None:
            parent.insertBefore(child, before_sibling)
        else:
            parent.appendChild(child)

    def remove_node_child(self, parent, child, destroy_node=True):
        parent.removeChild(child)
        if destroy_node:
            child.unlink()
