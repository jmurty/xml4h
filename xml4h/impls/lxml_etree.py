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

    def map_node_to_class(self, node):
        if isinstance(node, etree._ProcessingInstruction):
            return nodes.ProcessingInstruction
        elif isinstance(node, etree._Comment):
            return nodes.Comment
        elif isinstance(node, etree._ElementTree):
            return nodes.Document
        elif isinstance(node, etree._Element):
            return nodes.Element
        elif isinstance(node, etree.CDATA):
            return nodes.CDATA
        elif isinstance(node, LXMLAttribute):
            return nodes.Attribute
        elif isinstance(node, basestring):
            return nodes.Text
        raise Exception(
            'Unrecognized type for implementation node: %s' % node)

    def get_impl_root(self, node):
        return self._impl_document.getroot()

    # Document implementation methods

    def new_impl_element(self, tagname, ns_uri):
        return etree.Element(tagname)

    def new_impl_text(self, text):
        raise NotImplementedError()

    def new_impl_comment(self, text):
        return etree.Comment(text)

    def new_impl_instruction(self, target, data):
        return etree.ProcessingInstruction(target, data)

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
            # Ignore the current node
            if n == node:
                continue
            # Ignore non-Elements
            if not n.__class__ == etree._Element:
                continue
            if ns_uri != '*' and self.get_node_namespace_uri(n) != ns_uri:
                continue
            if name != '*' and self.get_node_local_name(n) != name:
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
        if isinstance(node, etree._ElementTree):
            return None
        else:
            parent = node.getparent()
            # Return ElementTree as root element's parent
            if parent is None:
                return self.impl_document
            return parent

    def get_node_children(self, node):
        if isinstance(node, etree._ElementTree):
            return [node.getroot()]
        else:
            return node.getchildren()

    def get_node_name(self, node):
        if isinstance(node, basestring):
            return '#text'
        elif isinstance(node, etree.CDATA):
            return '#cdata-section'
        elif isinstance(node, etree._Comment):
            return '#comment'
        elif isinstance(node, etree._ProcessingInstruction):
            return node.target
        elif node.prefix is not None:
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
        return node.value

    def set_node_value(self, node, value):
        node.value = value

    def get_node_text(self, node):
        return node.text

    def set_node_text(self, node, text):
        node.text = text

    def get_node_attributes(self, element, ns_uri=None):
        # TODO: Filter by ns_uri
        attribs = []
        for n, v in element.attrib.items():
            attribs.append(LXMLAttribute(n, v, element))
        # Include namespace declarations, which should also be attributes
        if element.nsmap:
            # TODO Exclude namespace items defined by parent
            for n, v in element.nsmap.items():
                # Only add namespace as attribute if not defined in parent
                if self._is_ns_in_ancestor(element, n, v):
                    continue
                if n is None:
                    attr_name = 'xmlns'
                else:
                    attr_name = 'xmlns:%s' % n
                attribs.append(LXMLAttribute(attr_name, v, element))
        return attribs

    def has_node_attribute(self, element, name, ns_uri=None):
        return name in [a.qname for a
                        in self.get_node_attributes(element, ns_uri)]

    def get_node_attribute_node(self, element, name, ns_uri=None):
        for attr in self.get_node_attributes(element, ns_uri):
            if attr.qname == name:
                return attr
        return None

    def get_node_attribute_value(self, element, name, ns_uri=None):
        if ns_uri is not None:
            prefix = self.lookup_ns_prefix_for_uri(element, ns_uri)
            name = '%s:%s' % (prefix, name)
        for attr in self.get_node_attributes(element, ns_uri):
            if attr.qname == name:
                return attr.value
        return None

    def set_node_attribute_value(self, element, name, value, ns_uri=None):
        if ns_uri is not None:
            if ':' in name:
                prefix, name = name.split(':')
            name = '{%s}%s' % (ns_uri, name)
        elif ':' in name:
            prefix, name = name.split(':')
            ns_uri = self.lookup_ns_uri_by_attr_name(element, prefix)
            name = '{%s}%s' % (ns_uri, name)
        # For lxml, namespace definitions are not applied as attributes
        if name.startswith('{%s}' % nodes.Node.XMLNS_URI):
            prefix = name.split('}')[1]
            if prefix == 'xmlns':
                prefix = None
            element.nsmap[prefix] = value
        else:
            element.attrib[name] = value

    def remove_node_attribute(self, element, name, ns_uri=None):
        if ns_uri is not None:
            name = '{%s}%s' % (ns_uri, name)
        elif ':' in name:
            prefix, name = name.split(':')
            if prefix == 'xmlns':
                prefix = None
            name = '{%s}%s' % (element.nsmap[prefix], name)
        if name in element.attrib:
            del(element.attrib[name])

    def add_node_child(self, parent, child, before_sibling=None):
        parent.append(child)

    def remove_node_child(self, parent, child, destroy_node=True):
        if destroy_node:
            child.clear()
        parent.remove(child)

    def lookup_ns_uri_by_attr_name(self, node, name):
        if name == 'xmlns':
            name = None
        elif name.startswith('xmlns:'):
            _, name = name.split(':')
        if name in node.nsmap:
            return node.nsmap[name]
        return None

    def lookup_ns_prefix_for_uri(self, node, uri):
        if uri in node.nsmap.values():
            for n, v in node.nsmap.items():
                if v == uri:
                    return n
        return None

    def _is_ns_in_ancestor(self, node, name, value):
        '''
        Return True if the given namespace name/value is defined in an
        ancestor of the given node, meaning that the given node need not
        have its own attributes to apply that namespacing.
        '''
        curr_node = self.get_node_parent(node)
        while curr_node is not None:
            if (hasattr(curr_node, 'nsmap')
                    and name in curr_node.nsmap
                    and curr_node.nsmap[name] == value):
                return True
            curr_node = self.get_node_parent(curr_node)
        return False


class LXMLAttribute(object):

    def __init__(self, name, value, element):
        self._name, self._value, self._element = name, value, element
        # Determine attribute's namespace and prefix
        self._ns_uri = None
        self._prefix = None
        if '}' in self.tag:
            self._ns_uri = self._name.split('}')[0][1:]
            self._name = self._name.split('}')[1]
            # Attribute is namespaced, find prefix defined for its URI
            if element.nsmap:
                for n, v in element.nsmap.items():
                    if self._ns_uri == v:
                        self._prefix = n
                        break;
        elif self._name == 'xmlns':
            self._ns_uri = nodes.Node.XMLNS_URI
        elif self._name.startswith('xmlns:'):
            self._ns_uri = nodes.Node.XMLNS_URI
        if ':' in self._name:
            self._prefix, self._name = self._name.split(':')
            #self._ns_uri = element.nsmap['xmlns:%s' % self._name]

    def getroottree(self):
        return self._element.getroottree()

    @property
    def prefix(self):
        return self._prefix

    @property
    def tag(self):
        return self._name

    name = tag  # Alias

    @property
    def qname(self):
        if self.prefix:
            return '%s:%s' % (self.prefix, self.name)
        else:
            return self.name

    @property
    def value(self):
        return self._value

    @property
    def namespace_uri(self):
        return self._ns_uri

