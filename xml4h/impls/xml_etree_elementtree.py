import re
import copy

import six

from xml4h.impls.interface import XmlImplAdapter
from xml4h import nodes, exceptions

# Import the pure-Python ElementTree implementation, if possible
try:
    import xml.etree.ElementTree as PythonET
    # Re-import non-C ElementTree with a definitive name, for cases where we
    # must explicilty use non-C-based elements of ElementTree.
    import xml.etree.ElementTree as BaseET
except ImportError:
    pass

# Import the C-based ElementTree implementation, if possible
try:
    import xml.etree.cElementTree as cET
except ImportError:
    pass


class ElementTreeAdapter(XmlImplAdapter):
    """
    Adapter to the
    `ElementTree <http://docs.python.org/2/library/xml.etree.elementtree.html>`_
    XML library.

    This code *must* work with either the base ElementTree pure python
    implementation or the C-based cElementTree implementation, since it is
    reused in the `cElementTree` class defined below.
    """

    ET = PythonET  # Use the pure-Python implementation

    SUPPORTED_FEATURES = {
        'xpath': True,
        }

    @classmethod
    def is_available(cls):
        # Is vital piece of ElementTree module available at all?
        try:
            cls.ET.Element
        except:
            return False
        # We only support ElementTree version 1.3+
        from distutils.version import StrictVersion
        return StrictVersion(BaseET.VERSION) >= StrictVersion('1.3')

    @classmethod
    def parse_string(cls, xml_str, ignore_whitespace_text_nodes=True):
        return cls.parse_file(
            six.StringIO(xml_str),
            ignore_whitespace_text_nodes=ignore_whitespace_text_nodes)

    @classmethod
    def parse_bytes(cls, xml_bytes, ignore_whitespace_text_nodes=True):
        return cls.parse_file(
            six.BytesIO(xml_bytes),
            ignore_whitespace_text_nodes=ignore_whitespace_text_nodes)

    @classmethod
    def parse_file(cls, xml_file_path, ignore_whitespace_text_nodes=True):
        # To retain explicit xmlns namespace definition attributes, we need to
        # manually add these elements to the parsed DOM as we go using
        # iterative parsing per:
        # effbot.org/zone/element-namespaces.htm#preserving-existing-namespace-attributes
        events = ('start', 'start-ns')
        impl_root = None
        ns_list = []
        for event, node in cls.ET.iterparse(xml_file_path, events):
            if event == 'start-ns':
                # Track namespaces as nodes declared
                ns_list.append(node)
            elif event == 'start':
                # Recognise and retain root node
                if impl_root is None:
                    impl_root = node
                # Add xmlns attributes for each namespace declared
                for ns_prefix, ns_uri in ns_list:
                    if ns_prefix:
                        attr_name = 'xmlns:%s' % ns_prefix
                    else:
                        attr_name = 'xmlns'
                    node.set(attr_name, ns_uri)
                # Reset namespace list now the corresponding attributes exist
                ns_list = []

        impl_doc = cls.ET.ElementTree(impl_root)
        wrapped_doc = cls.wrap_document(impl_doc)
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
        root_elem = cls.ET.Element('{%s}%s' % (ns_uri, root_tagname))
        doc = cls.ET.ElementTree(root_elem)
        return doc

    # This method is called by interface super-class's __init__
    def clear_caches(self):
        self.CACHED_ANCESTRY_DICT = {}

    def _lookup_node_parent(self, node):
        """
        Return the parent of the given node, based on an internal dictionary
        mapping of child nodes to the child's parent required since
        ElementTree doesn't make info about node ancestry/parentage available.
        """
        # Basic caching of our internal ancestry dict to help performance
        if not node in self.CACHED_ANCESTRY_DICT:
            # Given node isn't in cached ancestry dictionary, rebuild this now
            ancestry_dict = dict(
                (c, p) for p in self._impl_document.getiterator() for c in p)
            self.CACHED_ANCESTRY_DICT = ancestry_dict
        return self.CACHED_ANCESTRY_DICT[node]

    def _is_node_an_element(self, node):
        """
        Return True if the given node is an ElementTree Element, a fact that
        can be tricky to determine if the cElementTree implementation is
        used.
        """
        # Try the simplest approach first, works for plain old ElementTree
        if isinstance(node, BaseET.Element):
            return True
        # For cElementTree we need to be more cunning (or find a better way)
        if hasattr(node, 'makeelement') \
                and isinstance(node.tag, six.string_types):
            return True

    def map_node_to_class(self, node):
        if isinstance(node, BaseET.ElementTree):
            return nodes.Document
        elif node.tag == BaseET.ProcessingInstruction:
            return nodes.ProcessingInstruction
        elif node.tag == BaseET.Comment:
            return nodes.Comment
        elif isinstance(node, ETAttribute):
            return nodes.Attribute
        elif isinstance(node, ElementTreeText):
            if node.is_cdata:
                return nodes.CDATA
            else:
                return nodes.Text
        elif self._is_node_an_element(node):
            return nodes.Element
        raise exceptions.Xml4hImplementationBug(
            'Unrecognized type for implementation node: %s' % node)

    def get_impl_root(self, node):
        return self._impl_document.getroot()

    # Document implementation methods

    def new_impl_element(self, tagname, ns_uri=None, parent=None):
        if ns_uri is not None:
            if ':' in tagname:
                tagname = tagname.split(':')[1]
            element = self.ET.Element('{%s}%s' % (ns_uri, tagname))
            return element
        else:
            return self.ET.Element(tagname)

    def new_impl_text(self, text):
        return ElementTreeText(text)

    def new_impl_comment(self, text):
        return self.ET.Comment(text)

    def new_impl_instruction(self, target, data):
        return self.ET.ProcessingInstruction(target, data)

    def new_impl_cdata(self, text):
        return ElementTreeText(text, is_cdata=True)

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
            if not isinstance(n.tag, six.string_types):
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
        namespaces_dict = {}
        if 'namespaces' in kwargs:
            namespaces_dict.update(kwargs['namespaces'])
        # Empty namespace prefix is not supported, convert to '_' prefix
        if None in namespaces_dict:
            default_ns_uri = namespaces_dict.pop(None)
            namespaces_dict['_'] = default_ns_uri
        # If no default namespace URI defined, use root's namespace (if any)
        if not '_' in namespaces_dict:
            root = self.get_impl_root(node)
            qname, ns_uri, prefix, local_name = self._unpack_name(
                root.tag, root)
            if ns_uri:
                namespaces_dict['_'] = ns_uri
        # Include XMLNS namespace if it's not already defined
        if not 'xmlns' in namespaces_dict:
            namespaces_dict['xmlns'] = nodes.Node.XMLNS_URI
        return node.findall(xpath, namespaces_dict)

    # Node implementation methods

    def get_node_namespace_uri(self, node):
        if '}' in node.tag:
            return node.tag.split('}')[0][1:]
        elif isinstance(node, ETAttribute):
            return node.namespace_uri
        elif self._is_node_an_element(node):
            qname, ns_uri = self._unpack_name(node.tag, node)[:2]
            return ns_uri
        else:
            return None

    def set_node_namespace_uri(self, node, ns_uri):
        qname, orig_ns_uri, prefix, local_name = self._unpack_name(
            node.tag, node)
        node.tag = '{%s}%s' % (ns_uri, local_name)

    def get_node_parent(self, node):
        parent = None
        # Root document has no parent
        if isinstance(node, BaseET.ElementTree):
            pass
        elif hasattr(node, 'getparent'):
            parent = node.getparent()
        # Return ElementTree as root element's parent
        elif node == self.get_impl_root(node):
            parent = self._impl_document
        else:
            parent = self._lookup_node_parent(node)
        return parent

    def get_node_children(self, node):
        if isinstance(node, BaseET.ElementTree):
            children = [node.getroot()]
        else:
            if not hasattr(node, 'getchildren'):
                return []
            children = list(node.getchildren())
            # Hack to treat text attribute as child text nodes
            if node.text is not None:
                children.insert(0, ElementTreeText(node.text, parent=node))
        return children

    def get_node_name(self, node):
        if node.tag == BaseET.Comment:
            return '#comment'
        elif node.tag == BaseET.ProcessingInstruction:
            name, target = node.text.split(' ')
            return name
        prefix = self.get_node_name_prefix(node)
        if prefix is not None:
            return '%s:%s' % (prefix, self.get_node_local_name(node))
        else:
            return self.get_node_local_name(node)

    def get_node_local_name(self, node):
        return re.sub('{.*}', '', node.tag)

    def get_node_name_prefix(self, node):
        # Ignore non-elements
        if not isinstance(node.tag, six.string_types):
            return None
        # Believe nodes that have their own prefix (likely only ETAttribute)
        prefix = getattr(node, 'prefix', None)
        if prefix:
            return prefix
        # Derive prefix by unpacking node name
        qname, ns_uri, prefix, local_name = self._unpack_name(node.tag, node)
        if prefix:
            # Don't add unnecessary excess namespace prefixes for elements
            # with a local default namespace declaration
            if node.attrib.get('xmlns') == ns_uri:
                return None
            # Don't add unnecessary excess namespace prefixes for default ns
            elif prefix == 'xmlns':
                return None
            else:
                return prefix
        else:
            return None

    def get_node_value(self, node):
        if node.tag == BaseET.ProcessingInstruction:
            name, target = node.text.split(' ')
            return target
        elif node.tag == BaseET.Comment:
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
            attribs_by_qname[qname] = ETAttribute(
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
            prefix, local_name = name.split(':')
            if prefix != 'xmlns':
                ns_attr_name = 'xmlns:%s' % prefix
                ns_uri = self.lookup_ns_uri_by_attr_name(element, ns_attr_name)
                name = '{%s}%s' % (ns_uri, local_name)
        if name in element.attrib:
            del(element.attrib[name])

    def add_node_child(self, parent, child, before_sibling=None):
        if isinstance(child, ElementTreeText):
            # Add text values directly to parent's 'text' attribute
            if parent.text is not None:
                parent.text = parent.text + child.text
            else:
                parent.text = child.text
            self.CACHED_ANCESTRY_DICT[child] = parent
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
            self.CACHED_ANCESTRY_DICT[child] = parent
            return child

    def import_node(self, parent, node, original_parent=None, clone=False):
        original_node = node
        # We always clone for (c)ElementTree adapter so we can remove original
        # if necessary
        node = self.clone_node(node)
        self.add_node_child(parent, node)
        # Hack to remove text node content from original parent by manually
        # deleting matching text content
        if not clone:
            if isinstance(original_node, ElementTreeText):
                original_parent = self.get_node_parent(original_node)
                if original_parent.text == original_node.text:
                    # Must set to None if there would be no remaining text,
                    # otherwise parent element won't realise it's empty
                    original_parent.text = None
                else:
                    original_parent.text = \
                        original_parent.text.replace(original_node.text, '', 1)
            else:
                original_parent.remove(original_node)

    def clone_node(self, node, deep=True):
        if deep:
            return copy.deepcopy(node)
        else:
            return copy.copy(node)

    def remove_node_child(self, parent, child, destroy_node=True):
        if isinstance(child, ElementTreeText):
            child._parent.text = None
            return
        parent.remove(child)
        if destroy_node:
            child.clear()
            return None
        else:
            return child

    def lookup_ns_uri_by_attr_name(self, node, name):
        curr_node = node
        while (curr_node is not None
                and not isinstance(curr_node, BaseET.ElementTree)):
            uri = self.get_node_attribute_value(curr_node, name)
            if uri is not None:
                return uri
            curr_node = self.get_node_parent(curr_node)
        return None

    def lookup_ns_prefix_for_uri(self, node, uri):
        if uri == nodes.Node.XMLNS_URI:
            return 'xmlns'
        result = None
        # Lookup namespace URI in ET's awful global namespace/prefix registry
        if hasattr(BaseET, '_namespace_map') and uri in BaseET._namespace_map:
            result = BaseET._namespace_map[uri]
            if result == '':
                result = None
        if result is None or re.match('ns\d', result):
            # We either have no namespace prefix in the global mapping, in
            # which case we will try looking for a matching xmlns attribute,
            # or we have a namespace prefix that was probably assigned
            # automatically by ElementTree and we'd rather use a
            # human-assigned prefix if available.
            curr_node = node
            while self._is_node_an_element(curr_node):
                for n, v in list(curr_node.attrib.items()):
                    if v == uri:
                        if n.startswith('xmlns:'):
                            result = n.split(':')[1]
                            return result
                        elif n.startswith('{%s}' % nodes.Node.XMLNS_URI):
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


class ElementTreeText(object):

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


class ETAttribute(object):

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


class cElementTreeAdapter(ElementTreeAdapter):
    """
    Adapter to the C-based implementation of the
    `ElementTree <http://docs.python.org/2/library/xml.etree.elementtree.html>`_
    XML library.
    """

    ET = cET  # Use the C-based implementation

    @classmethod
    def is_available(cls):
        if not super(cElementTreeAdapter, cls).is_available():
            return False
        # We only support cElementTree version 1.0.6+
        from distutils.version import StrictVersion
        return StrictVersion(cls.ET.VERSION) >= StrictVersion('1.0.6')
