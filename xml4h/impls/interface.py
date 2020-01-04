import abc
import six

from xml4h import nodes, exceptions


@six.add_metaclass(abc.ABCMeta)
class XmlImplAdapter(object):
    """
    Base class that defines how *xml4h* interacts with an underlying XML
    library that the adaptor "wraps" to provide additional (or at least
    different) functionality.

    This class should be treated as an abstract class. It provides some
    common implementation code used by all *xml4h* adapter implementations,
    but mostly it sketches out the methods the real implementaiton subclasses
    must provide.
    """

    # List of extra features supported (or not) by an adapter implementation
    SUPPORTED_FEATURES = {
        'xpath': False,
        }

    @classmethod
    def has_feature(cls, feature_name):
        """
        :return: *True* if a named feature is supported by this adapter.
        """
        return cls.SUPPORTED_FEATURES.get(feature_name.lower(), False)

    @classmethod
    def ignore_whitespace_text_nodes(cls, wrapped_node):
        """
        Find and delete any text nodes containing nothing but whitespace in
        in the given node and its descendents.

        This is useful for cleaning up excess low-value text nodes in a
        document DOM after parsing a pretty-printed XML document.
        """
        for child in wrapped_node.children:
            if child.is_text and child.value.strip() == '':
                child.delete()
            else:
                cls.ignore_whitespace_text_nodes(child)

    @classmethod
    def create_document(cls, root_tagname, ns_uri=None, **kwargs):
        # Use implementation's method to create base document and root element
        impl_doc = cls.new_impl_document(root_tagname, ns_uri, **kwargs)
        adapter = cls(impl_doc)
        wrapped_doc = nodes.Document(impl_doc, adapter)
        # Automatically add namespace URI to root Element as attribute
        if ns_uri is not None:
            adapter.set_node_attribute_value(wrapped_doc.root.impl_node,
                'xmlns', ns_uri, ns_uri=nodes.Node.XMLNS_URI)
        return wrapped_doc

    @classmethod
    def wrap_document(cls, document_node):
        adapter = cls(document_node)
        return nodes.Document(document_node, adapter)

    @classmethod
    def wrap_node(cls, node, document, adapter=None):
        if node is None:
            return None
        if adapter is None:
            adapter = cls(document)
        impl_class = adapter.map_node_to_class(node)
        return impl_class(node, adapter)

    @classmethod
    @abc.abstractmethod
    def is_available(cls):
        """
        :return: *True* if this adapter's underlying XML library is available \
            in the Python environment.
        """
        raise NotImplementedError("Implementation missing for %s" % cls)

    @classmethod
    @abc.abstractmethod
    def parse_string(cls, xml_str, ignore_whitespace_text_nodes=True):
        raise NotImplementedError("Implementation missing for %s" % cls)

    @classmethod
    @abc.abstractmethod
    def parse_bytes(cls, xml_bytes, ignore_whitespace_text_nodes=True):
        raise NotImplementedError("Implementation missing for %s" % cls)

    @classmethod
    @abc.abstractmethod
    def parse_file(cls, xml_file, ignore_whitespace_text_nodes=True):
        raise NotImplementedError("Implementation missing for %s" % cls)

    def __init__(self, document):
        if not isinstance(document, object):
            raise exceptions.IncorrectArgumentTypeException(
                document, [object])
        self._impl_document = document
        self._auto_ns_prefix_count = 0
        self.clear_caches()

    def clear_caches(cls):
        """
        Clear any in-adapter cached data, for cases where cached data could
        become outdated e.g. by making DOM changes directly outside of *xml4h*.

        This is a no-op if the implementing adapter has no cached data.
        """
        pass

    @property
    def impl_document(self):
        return self._impl_document

    @property
    def impl_root_element(self):
        return self.get_impl_root(self.impl_document)

    def get_ns_uri_for_prefix(self, node, prefix):
        if prefix == 'xmlns':
            return nodes.Node.XMLNS_URI
        elif prefix is None:
            attr_name = 'xmlns'
        else:
            attr_name = 'xmlns:%s' % prefix
        uri = self.lookup_ns_uri_by_attr_name(node, attr_name)
        if uri is None:
            if attr_name == 'xmlns':
                # Default namespace URI
                return nodes.Node.XMLNS_URI
            raise exceptions.UnknownNamespaceException(
                "Unknown namespace URI for attribute name '%s'" % attr_name)
        return uri

    def get_ns_prefix_for_uri(self, node, uri, auto_generate_prefix=False):
        if uri == nodes.Node.XMLNS_URI:
            return 'xmlns'
        prefix = self.lookup_ns_prefix_for_uri(node, uri)
        if not prefix and auto_generate_prefix:
            prefix = 'autoprefix%d' % self._auto_ns_prefix_count
            self._auto_ns_prefix_count += 1
        return prefix

    def get_ns_info_from_node_name(self, name, impl_node):
        """
        Return a three-element tuple with the prefix, local name, and namespace
        URI for the given element/attribute name (in the context of the given
        node's hierarchy). If the name has no associated prefix or namespace
        information, None is return for those tuple members.
        """
        if '}' in name:
            ns_uri, name = name.split('}')
            ns_uri = ns_uri[1:]
            prefix = self.get_ns_prefix_for_uri(impl_node, ns_uri)
        elif ':' in name:
            prefix, name = name.split(':')
            ns_uri = self.get_ns_uri_for_prefix(impl_node, prefix)
            if ns_uri is None:
                raise exceptions.UnknownNamespaceException(
                    "Prefix '%s' does not have a defined namespace URI"
                    % prefix)
        else:
            prefix, ns_uri = None, None
        return prefix, name, ns_uri

    # Utility implementation methods

    @classmethod
    @abc.abstractmethod
    def new_impl_document(cls, root_tagname, ns_uri=None, **kwargs):
        raise NotImplementedError("Implementation missing for %s" % cls)

    @abc.abstractmethod
    def map_node_to_class(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_impl_root(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    # Document implementation methods

    @abc.abstractmethod
    def new_impl_element(self, tagname, ns_uri=None, parent=None):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def new_impl_text(self, text):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def new_impl_comment(self, text):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def new_impl_instruction(self, target, data):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def new_impl_cdata(self, text):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def find_node_elements(self, node, name='*', ns_uri='*'):
        """
        :return: element node descendents of the given node that match the \
            search constraints.

        :param node: a node object from the underlying XML library.
        :param string name: only elements with a matching name will be
            returned. If the value is ``*`` all names will match.
        :param string ns_uri: only elements with a matching namespace URI
            will be returned. If the value is ``*`` all namespaces will match.
        """
        raise NotImplementedError("Implementation missing for %s" % self)

    def xpath_on_node(self, node, xpath, **kwargs):
        if not self.has_feature('xpath'):
            raise exceptions.FeatureUnavailableException('xpath')

    # Node implementation methods

    @abc.abstractmethod
    def get_node_namespace_uri(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def set_node_namespace_uri(self, node, ns_uri):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_parent(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_children(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_name(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_local_name(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_name_prefix(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_value(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def set_node_value(self, node, value):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_text(self, node):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def set_node_text(self, node, text):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_attributes(self, element, ns_uri=None):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def has_node_attribute(self, element, name, ns_uri=None):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_attribute_node(self, element, name, ns_uri=None):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def get_node_attribute_value(self, element, name, ns_uri=None):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def set_node_attribute_value(self, element, name, value, ns_uri=None):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def remove_node_attribute(self, element, name, ns_uri=None):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def add_node_child(self, parent, child, before_sibling=None):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def import_node(self, parent, node, original_parent=None, clone=False):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def clone_node(self, node, deep=True):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def remove_node_child(self, parent, child, destroy_node=True):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def lookup_ns_uri_by_attr_name(self, node, name):
        raise NotImplementedError("Implementation missing for %s" % self)

    @abc.abstractmethod
    def lookup_ns_prefix_for_uri(self, node, uri):
        raise NotImplementedError("Implementation missing for %s" % self)
