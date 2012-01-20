import re

from xml4h.impls.interface import _XmlImplAdapter
from xml4h import nodes

from lxml import etree


class LXMLAdapter(_XmlImplAdapter):

    @classmethod
    def new_impl_document(cls, root_tagname, ns_uri=None, **kwargs):
        root_elem = etree.Element(root_tagname)
        doc = etree.ElementTree(root_elem)
        return doc

    @classmethod
    def get_impl_document(self, node):
        if isinstance(node, etree._ElementTree):  # TODO Weird!
            return node
        else:
            return node.getroottree()

    def map_node_to_class(self, node):
        if isinstance(node, etree._ElementTree):
            return nodes.Document
        elif hasattr(node, 'makeelement'):  # TODO
            return nodes.Element
        elif isinstance(node, LXMLAttribute):
            return nodes.Attribute
        raise Exception(
            'Unrecognized type for implementation node: %s' % node)

    def get_impl_root(self, node):
        return self.get_impl_document(node).getroot()

    # Document implementation methods

    def new_impl_element(self, tagname, ns_uri):
        return etree.Element(tagname)

    def new_impl_text(self, text):
        raise NotImplementedError()

    def new_impl_comment(self, text):
        raise NotImplementedError()

    def new_impl_instruction(self, target, data):
        raise NotImplementedError()

    def new_impl_cdata(self, text):
        raise NotImplementedError()

    def find_node_elements(self, node, name='*', ns_uri='*'):
        '''
        Return NodeList containing element node descendants of the given node
        which match the search constraints.

        If name is '*', elements with any name will be returned.
        If ns_uri is '*', elements in any namespace will be returned.
        '''
        # TODO Any proper way to find namespaced elements by name?
        name_match_nodes = node.getiterator()
        # Filter nodes by name and ns_uri if necessary
        results = []
        for n in name_match_nodes:
            if ns_uri != '*' and self.get_node_namespace_uri(n) != ns_uri:
                continue
            if name != '*' and self.get_node_name(n) != name:
                continue
            results.append(n)
        return results

    # Node implementation methods

    def get_node_namespace_uri(self, node):
        if isinstance(node, LXMLAttribute):
            return node.namespace_uri
        if '}' in node.tag:
            return node.tag.split('}')[0][1:]
        else:
            return None

    def set_node_namespace_uri(self, node, ns_uri):
        raise NotImplementedError()

    def get_node_parent(self, node):
        return node.getparent()

    def get_node_children(self, node):
        if isinstance(node, etree._ElementTree):
            return [node.getroot()]
        else:
            return node.getchildren()

    def get_node_name(self, node):
        if node.prefix is not None:
            return '%s:%s' % (node.prefix, self.get_node_local_name(node))
        else:
            return self.get_node_local_name(node)

    def set_node_name(self, node, name):
        raise NotImplementedError()

    def get_node_local_name(self, node):
        return re.sub('{.*}', '', node.tag)

    def get_node_name_prefix(self, node):
        return node.prefix

    def get_node_value(self, node):
        raise NotImplementedError()

    def set_node_value(self, node, value):
        raise NotImplementedError()

    def get_node_attributes(self, element, ns_uri=None):
        attribs = []
        for n, v in element.attrib.items():
            attribs.append(LXMLAttribute(n, v, element))
        # Include namespace declarations, which should also be attributes
        if element.nsmap:
            # TODO Exclude namespace items defined by parent
            for n, v in element.nsmap.items():
                if n is None:
                    attr_name = 'xmlns'
                else:
                    attr_name = 'xmlns:%s' % n
                attribs.append(LXMLAttribute(attr_name, v, element))
        return attribs

    def has_node_attribute(self, element, name, ns_uri=None):
        raise NotImplementedError()

    def get_node_attribute_node(self, element, name, ns_uri=None):
        raise NotImplementedError()

    def get_node_attribute_value(self, element, name, ns_uri=None):
        raise NotImplementedError()

    def set_node_attribute_value(self, element, name, value, ns_uri=None):
        raise NotImplementedError()

    def remove_node_attribute(self, element, name, ns_uri=None):
        raise NotImplementedError()

    def add_node_child(self, parent, child, before_sibling=None):
        parent.append(child)

    def remove_node_child(self, parent, child):
        raise NotImplementedError()


class LXMLAttribute(object):

    def __init__(self, name, value, element, ns_uri=None):
        self._name, self._value, self._element = name, value, element
        self._ns_uri = None

    def getroottree(self):
        return self._element.getroottree()

    @property
    def prefix(self):
        if ':' in self.tag:
            return self.tag.split(':')[0]
        else:
            return None

    @property
    def tag(self):
        return self._name

    @property
    def namespace_uri(self):
        if self._ns_uri is not None:
            return self._ns_uri
        elif self.tag == 'xmlns' or self.prefix == 'xmlns':
            return nodes.Node.XMLNS_URI
        else:
            return None

