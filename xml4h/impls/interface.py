from xml4h.nodes import Node, ElementNode


class _XmlImplWrapper(object):

    @classmethod
    def create(cls, root_tagname, namespace_uri=None, **kwargs):
        # Instantiate instance of implementation class
        self = cls()
        # Use implementation's method to create base document and root element
        impl_doc, impl_elem = self.create_doc_and_root_elem(
            root_tagname, namespace_uri, **kwargs)
        # Wrap root Element in a wrapper object
        root_element = ElementNode(impl_elem, impl_doc, self)
        # Assign document to wrapper
        self.impl_document = impl_doc
        # Automatically add namespace URI to root Element as attribute
        if namespace_uri is not None:
            self.set_node_attribute(
                impl_elem, 'xmlns', namespace_uri,
                namespace_uri='http://www.w3.org/2000/xmlns/')
        return root_element

    def create_doc_and_root_elem(cls, root_tagname,
            namespace_uri=None, **kwargs):
        raise NotImplementedError()

    # Utility implementation methods

    def wrap_impl_node(self, impl_node, impl_document, impl_wrapper):
        raise NotImplementedError()

    def map_node_type(self, node):
        raise NotImplementedError()

    def get_root_element(self):
        raise NotImplementedError()

    # Document implementation methods

    def new_impl_element(self, tagname, namespace_uri):
        raise NotImplementedError()

    def new_impl_text(self, text):
        raise NotImplementedError()

    def new_impl_comment(self, text):
        raise NotImplementedError()

    def new_impl_instruction(self, target, data):
        raise NotImplementedError()

    def new_impl_cdata(self, text):
        raise NotImplementedError()

    # Node implementation methods

    def get_node_parent(self, node):
        raise NotImplementedError()

    def get_node_children(self, node, namespace_uri=None):
        raise NotImplementedError()

    def get_node_name(self, node):
        raise NotImplementedError()

    def get_node_value(self, node):
        raise NotImplementedError()

    def get_node_attributes(self, element, namespace_uri=None):
        raise NotImplementedError()

    def set_node_attribute(self, element, name, value, namespace_uri=None):
        raise NotImplementedError()

    def add_node_child(self, parent, child, before_sibling=None):
        raise NotImplementedError()
