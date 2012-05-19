import re

from xml4h import nodes


class _XmlImplAdapter(object):

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
    def wrap_node(cls, node, document):
        if node is None:
            return None
        adapter = cls(document)
        impl_class = adapter.map_node_to_class(node)
        return impl_class(node, adapter)

    def __init__(self, document):
        if not document:
            raise Exception(
                'Cannot instantiate adapter with invalid document: %s'
                % document)
        self._impl_document = document
        self._auto_ns_prefix_count = 0

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
            raise Exception(
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

    # Utility implementation methods

    @classmethod
    def new_impl_document(cls, root_tagname, ns_uri=None, **kwargs):
        raise NotImplementedError()

    def map_node_to_class(self, node):
        raise NotImplementedError()

    def get_impl_root(self, node):
        raise NotImplementedError()

    # Document implementation methods

    def new_impl_element(self, tagname, ns_uri):
        raise NotImplementedError()

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
        raise NotImplementedError()

    # Node implementation methods

    def get_node_namespace_uri(self, node):
        raise NotImplementedError()

    def set_node_namespace_uri(self, node, ns_uri):
        raise NotImplementedError()

    def get_node_parent(self, node):
        raise NotImplementedError()

    def get_node_children(self, node):
        raise NotImplementedError()

    def get_node_name(self, node):
        raise NotImplementedError()

    def set_node_name(self, node, name):
        raise NotImplementedError()

    def get_node_local_name(self, node):
        raise NotImplementedError()

    def get_node_name_prefix(self, node):
        raise NotImplementedError()

    def get_node_value(self, node):
        raise NotImplementedError()

    def set_node_value(self, node, value):
        raise NotImplementedError()

    def get_node_text(self, node):
        raise NotImplementedError()

    def set_node_text(self, node, text):
        raise NotImplementedError()

    def get_node_attributes(self, element, ns_uri=None):
        raise NotImplementedError()

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
        raise NotImplementedError()

    def remove_node_child(self, parent, child, destroy_node=True):
        raise NotImplementedError()

    def lookup_ns_uri_by_attr_name(self, node, name):
        raise NotImplementedError()

    def lookup_ns_prefix_for_uri(slef, node, uri):
        raise NotImplementedError()

