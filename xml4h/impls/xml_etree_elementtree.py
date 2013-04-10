import re
import copy

from xml4h.impls.interface import XmlImplAdapter
from xml4h import nodes

# Use faster C-basedcElementTree implementation if available
try:
    import xml.etree.cElementTree as ET
except ImportError:
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        pass

# Re-import non-C ElementTree with a definitive name
try:
    import xml.etree.ElementTree as BaseET
except ImportError:
    pass


class ElementTreeAdapter(XmlImplAdapter):
    """
    Adapter to the
    `ElementTree <http://docs.python.org/2/library/xml.etree.elementtree.html>`_
    XML library implementation.
    """

    SUPPORTED_FEATURES = {
        'xpath': True,
        }

    @classmethod
    def is_available(cls):
        try:
            ET.Element
            return True
        except:
            return False

    @classmethod
    def parse_string(cls, xml_str, ignore_whitespace_text_nodes=True):
        impl_root_elem = ET.fromstring(xml_str)
        wrapped_doc = ElementTreeAdapter.wrap_document(impl_root_elem.getroottree())
        if ignore_whitespace_text_nodes:
            cls.ignore_whitespace_text_nodes(wrapped_doc)
        return wrapped_doc

    @classmethod
    def parse_file(cls, xml_file_path, ignore_whitespace_text_nodes=True):
        impl_doc = ET.parse(xml_file_path)
        wrapped_doc = ElementTreeAdapter.wrap_document(impl_doc)
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
        root_elem = ET.Element('{%s}%s' % (ns_uri, root_tagname))
        doc = ET.ElementTree(root_elem)
        # Godawful global registration of namespace prefixes is the only option
        # supported by ET, so we'll handle this more sanely ourselves.
        doc._xml4h_nsmap = root_nsmap
        return doc

    @property
    def _ancestry_dict(self):
        """
        Return a dictionary mapping of child nodes to the child's parent,
        if any.

        We're forced to use this awful hack since ElementTree doesn't let us
        get to a child node's parent node, even in version 1.3.0 which
        should support this with XPath lookups but actually doesn't.
        """
        # TODO Cache (and live-update) this dict for better performance
        ancestry_dict = dict(
            (c, p) for p in self._impl_document.getiterator() for c in p)
        return ancestry_dict

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
        elif isinstance(node, BaseET.Element):
            return nodes.Element
        # TODO: More reliable & explicit way of detecting cElementTree Element?
        elif isinstance(node.tag, basestring):
            return nodes.Element
        raise Exception(
            'Unrecognized type for implementation node: %s' % node)

    def get_impl_root(self, node):
        return self._impl_document.getroot()

    # Document implementation methods

    def new_impl_element(self, tagname, ns_uri=None, parent=None):
        if ns_uri is not None:
            if ':' in tagname:
                tagname = tagname.split(':')[1]
            element = ET.Element('{%s}%s' % (ns_uri, tagname))
#            my_nsmap = {None: ns_uri}
#            element._xml4h_nsmap = my_nsmap
            return element
        else:
            return ET.Element(tagname)

    def new_impl_text(self, text):
        return ElementTreeText(text)

    def new_impl_comment(self, text):
        return ET.Comment(text)

    def new_impl_instruction(self, target, data):
        return ET.ProcessingInstruction(target, data)

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
            if not isinstance(n.tag, basestring):
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
#        if isinstance(node, ET.ElementTree):
#            # Document node lxml.ET.ElementTree has no nsmap, lookup root
#            root = self.get_impl_root(node)
#            namespaces_dict = root.nsmap.copy()
#        else:
#            namespaces_dict = node.nsmap.copy()
        namespaces_dict = {}
        if 'namespaces' in kwargs:
            namespaces_dict.update(kwargs['namespaces'])
        # Empty namespace prefix is not supported, convert to '_' prefix
        if None in namespaces_dict:
            default_ns_uri = namespaces_dict.pop(None)
            namespaces_dict['_'] = default_ns_uri
        # TODO: Fix/improve this awful hack!
        elif '}' in self._impl_document._root.tag:
            default_ns_uri = self._impl_document._root.tag.split('}')[0][1:]
            namespaces_dict['_'] = default_ns_uri
        # Include XMLNS namespace if it's not already defined
        if not 'xmlns' in namespaces_dict:
            namespaces_dict['xmlns'] = nodes.Node.XMLNS_URI
        # WARNING: Awful hacks ahead...
        munged_xpath = xpath
        munged_node = node
        force_include_root = False
        if xpath.startswith('/'):
            # ElementTree does not support absolute XPath queries on nodes
            munged_node = self._impl_document
            if xpath in ('/', '/*'):
                # Hack to lookup document root
                munged_xpath = '.'
            else:
                # Hack to work around 1.3-and-earlier bug on '/' xpaths
                # TODO Avoid using hack on post-1.3 versions?
                munged_xpath = '.' + xpath
                force_include_root = True
        result_nodes = munged_node.findall(
            munged_xpath, namespaces=namespaces_dict)
        # Need to manually remove non-Elements from result nodes
        result_nodes = [
            n for n in result_nodes if isinstance(n.tag, basestring)]
        if force_include_root:
            result_nodes = [self._impl_document.getroot()] + result_nodes
        return result_nodes

    # Node implementation methods

    def get_node_namespace_uri(self, node):
        if '}' in node.tag:
            return node.tag.split('}')[0][1:]
        elif isinstance(node, ETAttribute):
            return node.namespace_uri
        elif isinstance(node, BaseET.ElementTree):
            return None
        elif isinstance(node, BaseET.Element):
            qname, ns_uri = self._unpack_name(node.tag, node)[:2]
            return ns_uri
        else:
            return None

    def set_node_namespace_uri(self, node, ns_uri):
        if not hasattr(node, '_xml4h_nsmap'):
            node._xml4h_nsmap = {}
        node._xml4h_nsmap[None] = ns_uri

    def get_node_parent(self, node):
        parent = None
        # Root document has no parent
        if isinstance(node, BaseET.ElementTree):
            pass
        # Return ElementTree as root element's parent
        elif node == self.get_impl_root(node):
            parent = self._impl_document
        else:
            try:
                parent = self._ancestry_dict[node]
            except KeyError:
                pass
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
            return target
        prefix = self.get_node_name_prefix(node)
        if prefix is not None:
            return '%s:%s' % (prefix, self.get_node_local_name(node))
        else:
            return self.get_node_local_name(node)

    def set_node_name(self, node, name):
        raise NotImplementedError()

    def get_node_local_name(self, node):
        return re.sub('{.*}', '', node.tag)

    def get_node_name_prefix(self, node):
        # Ignore non-elements
        if not isinstance(node.tag, basestring):
            return None
        # Believe nodes that know their own prefix (likely only ETAttribute)
        if hasattr(node, 'prefix'):
            return node.prefix
        # TODO Centralise namespace/prefix recognition/extraction
        # Parse
        match = re.match(r'{(.*)}', node.tag)
        if match is None:
            return None
        else:
            ns_uri = match.group(1)
            return self.lookup_ns_prefix_for_uri(node, ns_uri)

    def get_node_value(self, node):
        if node.tag in (BaseET.ProcessingInstruction, BaseET.Comment):
            return node.text
        else:
            return node.value

    def set_node_value(self, node, value):
        node.value = value

    def get_node_text(self, node):
        return node.text

    def set_node_text(self, node, text):
        node.text = text

    def get_node_attributes(self, element, ns_uri=None):
        # TODO: Filter by ns_uri
        attribs_by_qname = {}
        for n, v in element.attrib.items():
            qname, ns_uri, prefix, local_name = self._unpack_name(n, element)
            attribs_by_qname[qname] = ETAttribute(
                qname, ns_uri, prefix, local_name, v, element)
        # Include namespace declarations, which we also treat as attributes
#        if element.nsmap:
#            for n, v in element.nsmap.items():
#                # Only add namespace as attribute if not defined in ancestors
#                # and not the global xmlns namespace
#                if (self._is_ns_in_ancestor(element, n, v)
#                        or v == nodes.Node.XMLNS_URI):
#                    continue
#                if n is None:
#                    ns_attr_name = 'xmlns'
#                else:
#                    ns_attr_name = 'xmlns:%s' % n
#                qname, ns_uri, prefix, local_name = self._unpack_name(
#                    ns_attr_name, element)
#                attribs_by_qname[qname] = ETAttribute(
#                    qname, ns_uri, prefix, local_name, v, element)
        return attribs_by_qname.values()

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
#            if element.nsmap.get(name) != value:
#                # Ideally we would apply namespace (xmlns) attributes to the
#                # element's `nsmap` only, but the lxml/etree nsmap attribute
#                # is immutable and there's no non-hacky way around this.
#                # TODO Is there a better way?
#                pass
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

    def import_node(self, parent, node, clone=False):
        original_node = node
        if clone:
            node = self.clone_node(node)
        self.add_node_child(parent, node)
        # Hack to remove text node content from original parent by manually
        # deleting matching text content
        if not clone and isinstance(original_node, ElementTreeText):
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
        if isinstance(child, ElementTreeText):
            parent.text = None
            return
        parent.remove(child)
        if destroy_node:
            child.clear()
            return None
        else:
            return child

    def lookup_ns_uri_by_attr_name(self, node, name):
        if name == 'xmlns':
            ns_name = None
        elif name.startswith('xmlns:'):
            _, ns_name = name.split(':')
#        if ns_name in node.nsmap:
#            return node.nsmap[ns_name]
#        # If namespace is not in `nsmap` it may be in an XML DOM attribute
#        # TODO Generalize this block
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
        elif hasattr(node, '_xml4h_nsmap') and uri in node._xml4h_nsmap.values():
            for n, v in node._xml4h_nsmap.items():
                if v == uri:
                    result = n
                    break
        if result is None or re.match('ns\d', result):
            # We either have no namespace prefix in the global mapping, in
            # which case we will try looking for a matching xmlns attribute,
            # or we have a namespace prefix that was probably assigned
            # automatically by ElementTree and we'd rather use a
            # human-assigned prefix if available.
            curr_node = node
            while curr_node.__class__ == BaseET.Element:
                for n, v in curr_node.attrib.items():
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

    def _is_ns_in_ancestor(self, node, name, value):
        """
        Return True if the given namespace name/value is defined in an
        ancestor of the given node, meaning that the given node need not
        have its own attributes to apply that namespacing.
        """
        curr_node = self.get_node_parent(node)
        while curr_node.__class__ == ET.Element:
            if (hasattr(curr_node, '_xml4h_nsmap')
                    and curr_node._xml4h_nsmap.get(name) == value):
                return True
            for n, v in curr_node.attrib.items():
                if v == value and '{%s}' % nodes.Node.XMLNS_URI in n:
                    return True
            curr_node = self.get_node_parent(curr_node)
        return False


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
