import re
import copy

from xml4h.impls.interface import XmlImplAdapter
from xml4h import nodes, exceptions

try:
    from lxml import etree
except ImportError:
    pass


class LXMLAdapter(XmlImplAdapter):
    """
    Adapter to the `lxml <http://lxml.de>`_ XML library implementation.
    """

    SUPPORTED_FEATURES = {
        'xpath': True,
        }

    @classmethod
    def is_available(cls):
        try:
            etree.Element
            return True
        except:
            return False

    @classmethod
    def parse_string(cls, xml_str, ignore_whitespace_text_nodes=True):
        impl_root_elem = etree.fromstring(xml_str)
        wrapped_doc = LXMLAdapter.wrap_document(impl_root_elem.getroottree())
        if ignore_whitespace_text_nodes:
            cls.ignore_whitespace_text_nodes(wrapped_doc)
        return wrapped_doc

    @classmethod
    def parse_bytes(cls, xml_bytes, ignore_whitespace_text_nodes=True):
        return LXMLAdapter.parse_string(xml_bytes, ignore_whitespace_text_nodes)

    @classmethod
    def parse_file(cls, xml_file, ignore_whitespace_text_nodes=True):
        impl_doc = etree.parse(xml_file)
        wrapped_doc = LXMLAdapter.wrap_document(impl_doc)
        if ignore_whitespace_text_nodes:
            cls.ignore_whitespace_text_nodes(wrapped_doc)
        return wrapped_doc

    @classmethod
    def new_impl_document(cls, root_tagname, ns_uri=None, **kwargs):
        root_nsmap = {}
        if ns_uri is not None:
            root_nsmap[None] = ns_uri
        else:
            ns_uri = nodes.Node.XMLNS_URI
            root_nsmap[None] = ns_uri
        root_elem = etree.Element('{%s}%s' % (ns_uri, root_tagname),
            nsmap=root_nsmap)
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
        elif isinstance(node, LXMLAttribute):
            return nodes.Attribute
        elif isinstance(node, LXMLText):
            if node.is_cdata:
                return nodes.CDATA
            else:
                return nodes.Text
        raise exceptions.Xml4hImplementationBug(
            'Unrecognized type for implementation node: %s' % node)

    def get_impl_root(self, node):
        return self._impl_document.getroot()

    # Document implementation methods

    def new_impl_element(self, tagname, ns_uri=None, parent=None):
        if ns_uri is not None:
            if ':' in tagname:
                tagname = tagname.split(':')[1]
            my_nsmap = {None: ns_uri}
            # Add any xmlns attribute prefix mappings from parent's document
            # TODO This doesn't seem to help
            curr_node = parent
            while curr_node.__class__ == etree._Element:
                for n, v in list(curr_node.attrib.items()):
                    if '{%s}' % nodes.Node.XMLNS_URI in n:
                        _, prefix = n.split('}')
                        my_nsmap[prefix] = v
                curr_node = self.get_node_parent(curr_node)
            return etree.Element('{%s}%s' % (ns_uri, tagname), nsmap=my_nsmap)
        else:
            return etree.Element(tagname)

    def new_impl_text(self, text):
        return LXMLText(text)

    def new_impl_comment(self, text):
        return etree.Comment(text)

    def new_impl_instruction(self, target, data):
        return etree.ProcessingInstruction(target, data)

    def new_impl_cdata(self, text):
        return LXMLText(text, is_cdata=True)

    def find_node_elements(self, node, name='*', ns_uri='*'):
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
    find_node_elements.__doc__ = XmlImplAdapter.find_node_elements.__doc__

    def xpath_on_node(self, node, xpath, **kwargs):
        """
        Return result of performing the given XPath query on the given node.

        All known namespace prefix-to-URI mappings in the document are
        automatically included in the XPath invocation.

        If an empty/default namespace (i.e. None) is defined, this is
        converted to the prefix name '_' so it can be used despite empty
        namespace prefixes being unsupported by XPath.
        """
        if isinstance(node, etree._ElementTree):
            # Document node lxml.etree._ElementTree has no nsmap, lookup root
            root = self.get_impl_root(node)
            namespaces_dict = root.nsmap.copy()
        else:
            namespaces_dict = node.nsmap.copy()
        if 'namespaces' in kwargs:
            namespaces_dict.update(kwargs['namespaces'])
        # Empty namespace prefix is not supported, convert to '_' prefix
        if None in namespaces_dict:
            default_ns_uri = namespaces_dict.pop(None)
            namespaces_dict['_'] = default_ns_uri
        # Include XMLNS namespace if it's not already defined
        if not 'xmlns' in namespaces_dict:
            namespaces_dict['xmlns'] = nodes.Node.XMLNS_URI
        return node.xpath(xpath, namespaces=namespaces_dict)

    # Node implementation methods

    def get_node_namespace_uri(self, node):
        if '}' in node.tag:
            return node.tag.split('}')[0][1:]
        elif isinstance(node, LXMLAttribute):
            return node.namespace_uri
        elif isinstance(node, etree._ElementTree):
            return None
        elif isinstance(node, etree._Element):
            qname, ns_uri = self._unpack_name(node.tag, node)[:2]
            return ns_uri
        else:
            return None

    def set_node_namespace_uri(self, node, ns_uri):
        node.nsmap[None] = ns_uri

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
            children = [node.getroot()]
        else:
            if not hasattr(node, 'getchildren'):
                return []
            children = node.getchildren()
            # Hack to treat text attribute as child text nodes
            if node.text is not None:
                children.insert(0, LXMLText(node.text, parent=node))
        return children

    def get_node_name(self, node):
        if isinstance(node, etree._Comment):
            return '#comment'
        elif isinstance(node, etree._ProcessingInstruction):
            return node.target
        prefix = self.get_node_name_prefix(node)
        local_name = self.get_node_local_name(node)
        if prefix is not None:
            return '%s:%s' % (prefix, local_name)
        else:
            return local_name

    def get_node_local_name(self, node):
        return re.sub('{.*}', '', node.tag)

    def get_node_name_prefix(self, node):
        # Believe non-Element nodes that have a prefix set (e.g. LXMLAttribute)
        if node.prefix and not isinstance(node, etree._Element):
            return node.prefix
        # Derive prefix by unpacking node name
        qname, ns_uri, prefix, local_name = self._unpack_name(node.tag, node)
        if prefix:
            # Don't add unnecessary excess namespace prefixes for elements
            # with a local default namespace declaration
            xmlns_val = self.get_node_attribute_value(node, 'xmlns')
            if xmlns_val == ns_uri:
                return None
            # Don't add unnecessary excess namespace prefixes for default ns
            if prefix == 'xmlns':
                return None
            else:
                return prefix
        else:
            return None

    def get_node_value(self, node):
        if isinstance(node, (etree._ProcessingInstruction, etree._Comment)):
            return node.text
        elif hasattr(node, 'value'):
            return node.value
        else:
            return node.text

    def set_node_value(self, node, value):
        if hasattr(node, 'value'):
            node.value = value
        else:
            self.set_node_text(node, value)

    def get_node_text(self, node):
        return node.text

    def set_node_text(self, node, text):
        node.text = text

    def get_node_attributes(self, element, ns_uri=None):
        # TODO: Filter by ns_uri
        attribs_by_qname = {}
        for n, v in list(element.attrib.items()):
            qname, ns_uri, prefix, local_name = self._unpack_name(n, element)
            attribs_by_qname[qname] = LXMLAttribute(
                qname, ns_uri, prefix, local_name, v, element)
        # Include namespace declarations, which we also treat as attributes
        if element.nsmap:
            for n, v in list(element.nsmap.items()):
                # Only add namespace as attribute if not defined in ancestors
                # and not the global xmlns namespace
                if (self._is_ns_in_ancestor(element, n, v)
                        or v == nodes.Node.XMLNS_URI):
                    continue
                if n is None:
                    ns_attr_name = 'xmlns'
                else:
                    ns_attr_name = 'xmlns:%s' % n
                qname, ns_uri, prefix, local_name = self._unpack_name(
                    ns_attr_name, element)
                attribs_by_qname[qname] = LXMLAttribute(
                    qname, ns_uri, prefix, local_name, v, element)
        return list(attribs_by_qname.values())

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
        prefix = None
        if ':' in name:
            prefix, name = name.split(':')
        if ns_uri is None and prefix is not None:
            ns_uri = self.lookup_ns_uri_by_attr_name(element, prefix)
        if ns_uri is not None:
            name = '{%s}%s' % (ns_uri, name)
        if name.startswith('{%s}' % nodes.Node.XMLNS_URI):
            if element.nsmap.get(name) != value:
                # Ideally we would apply namespace (xmlns) attributes to the
                # element's `nsmap` only, but the lxml/etree nsmap attribute
                # is immutable and there's no non-hacky way around this.
                # TODO Is there a better way?
                pass
            if name.split('}')[1] == 'xmlns':
                # Hack to remove namespace URI from 'xmlns' attributes so
                # the name is just a simple string
                name = 'xmlns'
            element.attrib[name] = value
        else:
            element.attrib[name] = value

    def remove_node_attribute(self, element, name, ns_uri=None):
        if ns_uri is not None:
            name = '{%s}%s' % (ns_uri, name)
        elif ':' in name:
            prefix, name = name.split(':')
            if prefix == 'xmlns':
                name = '{%s}%s' % (nodes.Node.XMLNS_URI, name)
            else:
                name = '{%s}%s' % (element.nsmap[prefix], name)
        if name in element.attrib:
            del(element.attrib[name])

    def add_node_child(self, parent, child, before_sibling=None):
        if isinstance(child, LXMLText):
            # Add text values directly to parent's 'text' attribute
            if parent.text is not None:
                parent.text = parent.text + child.text
            else:
                parent.text = child.text
            return None
        else:
            if before_sibling is not None:
                offset = 0
                for c in parent.getchildren():
                    if c == before_sibling:
                        break
                    offset += 1
                parent.insert(offset, child)
            else:
                parent.append(child)
            return child

    def import_node(self, parent, node, original_parent=None, clone=False):
        original_node = node
        if clone:
            node = self.clone_node(node)
        self.add_node_child(parent, node)
        # Hack to remove text node content from original parent by manually
        # deleting matching text content
        if not clone and isinstance(original_node, LXMLText):
            original_parent = self.get_node_parent(original_node)
            if original_parent.text == original_node.text:
                # Must set to None if there would be no remaining text,
                # otherwise parent element won't realise it's empty
                original_parent.text = None
            else:
                original_parent.text = \
                    original_parent.text.replace(original_node.text, '', 1)

    def clone_node(self, node, deep=True):
        if deep:
            return copy.deepcopy(node)
        else:
            return copy.copy(node)

    def remove_node_child(self, parent, child, destroy_node=True):
        if isinstance(child, LXMLText):
            parent.text = None
            return
        parent.remove(child)
        if destroy_node:
            child.clear()
            return None
        else:
            return child

    def lookup_ns_uri_by_attr_name(self, node, name):
        ns_name = None
        if name == 'xmlns':
            ns_name = None
        elif name.startswith('xmlns:'):
            _, ns_name = name.split(':')
        if ns_name in node.nsmap:
            return node.nsmap[ns_name]
        # If namespace is not in `nsmap` it may be in an XML DOM attribute
        # TODO Generalize this block
        curr_node = node
        while (curr_node is not None
                and curr_node.__class__ != etree._ElementTree):
            uri = self.get_node_attribute_value(curr_node, name)
            if uri is not None:
                return uri
            curr_node = self.get_node_parent(curr_node)
        return None

    def lookup_ns_prefix_for_uri(self, node, uri):
        if uri == nodes.Node.XMLNS_URI:
            return 'xmlns'
        result = None
        if hasattr(node, 'nsmap') and uri in list(node.nsmap.values()):
            for n, v in list(node.nsmap.items()):
                if v == uri:
                    result = n
                    break
        # TODO This is a slow hack necessary due to lxml's immutable nsmap
        if result is None or re.match('ns\d', result):
            # We either have no namespace prefix in the nsmap, in which case we
            # will try looking for a matching xmlns attribute, or we have
            # a namespace prefix that was probably assigned automatically by
            # lxml and we'd rather use a human-assigned prefix if available.
            curr_node = node  # self.get_node_parent(node)
            while curr_node.__class__ == etree._Element:
                for n, v in list(curr_node.attrib.items()):
                    if v == uri and ('{%s}' % nodes.Node.XMLNS_URI) in n:
                        result = n.split('}')[1]
                        return result
                curr_node = self.get_node_parent(curr_node)
        return result

    def _unpack_name(self, name, node):
        qname = prefix = local_name = ns_uri = None
        if name == 'xmlns':
            # Namespace URI of 'xmlns' is a constant
            ns_uri = nodes.Node.XMLNS_URI
        elif '}' in name:
            # Namespace URI is contained in {}, find URI's defined prefix
            ns_uri, local_name = name.split('}')
            ns_uri = ns_uri[1:]
            prefix = self.lookup_ns_prefix_for_uri(node, ns_uri)
        elif ':' in name:
            # Namespace prefix is before ':', find prefix's defined URI
            prefix, local_name = name.split(':')
            if prefix == 'xmlns':
                # All 'xmlns' attributes are in XMLNS URI by definition
                ns_uri = nodes.Node.XMLNS_URI
            else:
                ns_uri = self.lookup_ns_uri_by_attr_name(node, prefix)
        # Catch case where a prefix other than 'xmlns' points at XMLNS URI
        if name != 'xmlns' and ns_uri == nodes.Node.XMLNS_URI:
            prefix = 'xmlns'
        # Construct fully-qualified name from prefix + local names
        if prefix is not None:
            qname = '%s:%s' % (prefix, local_name)
        else:
            qname = local_name = name
        return (qname, ns_uri, prefix, local_name)

    def _is_ns_in_ancestor(self, node, name, value):
        """
        Return True if the given namespace name/value is defined in an
        ancestor of the given node, meaning that the given node need not
        have its own attributes to apply that namespacing.
        """
        curr_node = self.get_node_parent(node)
        while curr_node.__class__ == etree._Element:
            if (hasattr(curr_node, 'nsmap')
                    and curr_node.nsmap.get(name) == value):
                return True
            for n, v in list(curr_node.attrib.items()):
                if v == value and '{%s}' % nodes.Node.XMLNS_URI in n:
                    return True
            curr_node = self.get_node_parent(curr_node)
        return False


class LXMLText(object):

    def __init__(self, text, parent=None, is_cdata=False):
        self._text = text
        self._parent = parent
        self._is_cdata = is_cdata

    @property
    def is_cdata(self):
        return self._is_cdata

    @property
    def value(self):
        return self._text

    text = value  # Alias

    def getparent(self):
        return self._parent

    @property
    def prefix(self):
        return None

    @property
    def tag(self):
        if self.is_cdata:
            return "#cdata-section"
        else:
            return "#text"


class LXMLAttribute(object):

    def __init__(self, qname, ns_uri, prefix, local_name, value, element):
        self._qname, self._ns_uri, self._prefix, self._local_name = (
            qname, ns_uri, prefix, local_name)
        self._value, self._element = (value, element)

    def getroottree(self):
        return self._element.getroottree()

    @property
    def qname(self):
        return self._qname

    @property
    def namespace_uri(self):
        return self._ns_uri

    @property
    def prefix(self):
        return self._prefix

    @property
    def local_name(self):
        return self._local_name

    @property
    def value(self):
        return self._value

    name = tag = local_name  # Alias
