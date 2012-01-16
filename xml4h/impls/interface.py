from xml4h.nodes import Node, Element


class _XmlImplWrapper(object):

    @classmethod
    def create_document(cls, root_tagname, ns_uri=None, **kwargs):
        # Use implementation's method to create base document and root element
        impl_doc = cls.new_impl_document(root_tagname, ns_uri, **kwargs)
        wrapper = cls(impl_doc)
        # Wrap root Element in a wrapper object
        wrapped_root_element = Element(wrapper.impl_root_element, wrapper)
        # Automatically add namespace URI to root Element as attribute
        if ns_uri is not None:
            wrapper.set_node_attribute(wrapper.impl_root_element,
                'xmlns', ns_uri, ns_uri=Node.XMLNS_URI)
        return wrapped_root_element

    @classmethod
    def wrap_document(cls, document):
        wrapper = cls(document)
        return Element(wrapper.impl_root_element, wrapper)

    @classmethod
    def wrap_node(cls, node):
        wrapper = cls(cls.get_impl_document(node))
        return Element(node, wrapper)

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

    def wrap_impl_node(self, impl_node):
        raise NotImplementedError()

    def map_node_type(self, node):
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
