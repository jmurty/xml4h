from xml4h import nodes


class _XmlImplWrapper(object):

    @classmethod
    def create_document(cls, root_tagname, ns_uri=None, **kwargs):
        # Use implementation's method to create base document and root element
        impl_doc = cls.new_impl_document(root_tagname, ns_uri, **kwargs)
        wrapper = cls(impl_doc)
        wrapped_doc = nodes.Document(impl_doc, wrapper)
        # Automatically add namespace URI to root Element as attribute
        if ns_uri is not None:
            wrapper.set_node_attribute(wrapped_doc.root.impl_node,
                'xmlns', ns_uri, ns_uri=nodes.Node.XMLNS_URI)
        return wrapped_doc

    @classmethod
    def wrap_document(cls, document):
        wrapper = cls(document)
        return nodes.Document(document, wrapper)

    @classmethod
    def wrap_node(cls, node, document=None):
        # Use document if it's provided rather than looking it up
        if document is not None:
            wrapper = cls(document)
        else:
            wrapper = cls(cls.get_impl_document(node))
        impl_class = wrapper.map_node_to_class(node)
        return impl_class(node, wrapper)

    @classmethod
    def get_impl_document(self, node):
        return node.ownerDocument

    def __init__(self, document):
        self._impl_document = document

    @property
    def impl_document(self):
        return self._impl_document

    @property
    def impl_root_element(self):
        return self.impl_document.documentElement

    # Utility implementation methods

    @classmethod
    def new_impl_document(cls, root_tagname, ns_uri=None, **kwargs):
        raise NotImplementedError()

    def map_node_to_class(self, node):
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

    def get_node_parent(self, node):
        raise NotImplementedError()

    def get_node_children(self, node, ns_uri=None):
        raise NotImplementedError()

    def get_node_name(self, node):
        raise NotImplementedError()

    def get_node_value(self, node):
        raise NotImplementedError()

    def get_node_attributes(self, element, ns_uri=None):
        raise NotImplementedError()

    def set_node_attribute(self, element, name, value, ns_uri=None):
        raise NotImplementedError()

    def add_node_child(self, parent, child, before_sibling=None):
        raise NotImplementedError()

    def remove_node_child(self, parent, child):
        raise NotImplementedError()

