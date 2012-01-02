class Node(object):

    def __init__(self, element, document):
        if document is None or element is None:
            raise Exception('Cannot instantiate without element and document')
        self._element = element
        self._document = document

    @property
    def element(self):
        return self._element

    @property
    def document(self):
        return self._document

    def __eq__(self, other):
        if self is other:
            return True
        return self.document == getattr(other, 'document')

    # Methods that operate on underlying DOM implementation

    def _new_element_node(self, tagname, namespace_uri):
        raise NotImplementedError()

    def _new_text_node(self, text):
        raise NotImplementedError()

    def _new_comment_node(self, text):
        raise NotImplementedError()

    def _new_processing_instruction_node(self, target, data):
        raise NotImplementedError()

    def _new_cdata_node(self, text):
        raise NotImplementedError()

    def _get_parent(self, element):
        raise NotImplementedError()

    def _get_root_element(self):
        raise NotImplementedError()

    # Methods that operate on this Node implementation wrapper

    def write(self, writer, encoding='utf-8',
            indent=0, newline='\n', omit_declaration=False):
        raise NotImplementedError()

    def xml(self, encoding='utf-8',
            indent=4, newline='\n', omit_declaration=False):
        raise NotImplementedError()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.xml()


class NamedNode(Node):

    def _get_tagname(self, element):
        raise NotImplementedError()

    def _set_tagname(self, element, name):
        raise NotImplementedError()


    def get_name(self):
        return self._get_tagname(self.element)

    def set_name(self, name):
        self._set_tagname(self.element, name)

    name = property(get_name, set_name)


class ElementNode(NamedNode):
    '''
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.
    '''

    @classmethod
    def create(cls, root_tagname, namespace_uri=None):
        raise NotImplementedError()

    def _add_child_node(self, parent, child, before_sibling=None):
        raise NotImplementedError()

    def _set_attribute(self, element, name, value, namespace_uri=None):
        raise NotImplementedError()

    @property
    def klass(self):
        return self.__class__

    @property
    def root(self):
        return self.klass(self._get_root_element(), self.document)

    def up(self, count=1, to_tagname=None):
        elem = self.element
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if (self._get_parent(elem) is None
                    or self._get_parent(elem) == self.document):
                return self.klass(self._get_root_element(), self.document)
            elem = self._get_parent(elem)
            if to_tagname is None:
                up_count += 1
                if up_count >= count:
                    break
            else:
                if self._get_tagname(elem) == to_tagname:
                    break
        return self.klass(elem, self.document)

    def add_element(self, tagname, namespace_uri=None,
            attributes=None, text=None, before=False):
        elem = self._new_element_node(tagname, namespace_uri)
        # Automatically add namespace URI to Element as attribute
        if namespace_uri is not None:
            self._set_namespace(elem, namespace_uri)
        if attributes is not None:
            self._set_attributes(elem, attr_obj=attributes)
        if text is not None:
            self._add_text(elem, text=text)
        if before:
            self._add_child_node(
                self._get_parent(self.element), elem,
                before_sibling=self.element)
        else:
            self._add_child_node(self.element, elem)
        return self.klass(elem, self.document)

    add_elem = add_element  # Alias

    add_e = add_element  # Alias

    def _set_attributes(self, element,
            attr_obj=None, namespace_uri=None, **attr_dict):
        if attr_obj is not None:
            if isinstance(attr_obj, dict):
                attr_dict.update(attr_obj)
            elif isinstance(attr_obj, list):
                for n, v in attr_obj:
                    attr_dict[n] = v
            else:
                raise Exception('Attribute data must be a dictionary or list')
        for n, v in attr_dict.items():
            if ' ' in n:
                raise Exception("Invalid attribute name value contains space")
            if not isinstance(v, basestring):
                v = unicode(v)
            self._set_attribute(element, n, v, namespace_uri=namespace_uri)

    def set_attributes(self, attr_obj=None, namespace_uri=None, **attr_dict):
        self._set_attributes(self.element,
            attr_obj=attr_obj, namespace_uri=namespace_uri, **attr_dict)
        return self

    set_attrs = set_attributes  # Alias

    set_as = set_attributes  # Alias

    def _add_text(self, element, text):
        text_node = self._new_text_node(text)
        element.appendChild(text_node)

    def add_text(self, text):
        self._add_text(self.element, text)
        return self

    add_t = add_text  # Alias

    # TODO set_text : replaces any existing text nodes

    def _add_comment(self, element, text):
        comment_node = self._new_comment_node(text)
        element.appendChild(comment_node)

    def add_comment(self, text):
        self._add_comment(self.element, text)
        return self

    add_c = add_comment  # Alias

    def _add_instruction(self, element, target, data):
        instruction_node = self._new_processing_instruction_node(target, data)
        element.appendChild(instruction_node)

    def add_instruction(self, target, data):
        self._add_instruction(self.element, target, data)
        return self

    add_processing_instruction = add_instruction  # Alias

    add_i = add_instruction  # Alias

    def _set_namespace(self, element, namespace_uri, prefix=None):
        if not prefix:
            ns_name = 'xmlns'
        else:
            ns_name = 'xmlns:%s' % prefix
        self._set_attributes(element,
            {ns_name: namespace_uri},
            namespace_uri='http://www.w3.org/2000/xmlns/')

    def set_namespace(self, namespace_uri, prefix=None):
        self._set_namespace(self.element, namespace_uri, prefix=prefix)
        return self

    set_ns = set_namespace  # Alias

    def _add_cdata(self, dlement, data):
        cdata_node = self._new_cdata_node(data)
        element.appendChild(cdata_node)

    def add_cdata(self, data):
        self._add_cdata(self.element, data)
        return self

    add_data = add_cdata  # Alias

    add_d = add_cdata  # Alias


