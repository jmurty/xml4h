import codecs
from StringIO import StringIO


class Node(object):
    XMLNS_URI = 'http://www.w3.org/2000/xmlns/'

    ELEMENT = 1
    ATTRIBUTE = 2
    TEXT = 3
    CDATA = 4
    ENTITY = 5
    PROCESSING_INSTRUCTION = 6
    COMMENT = 7
    DOCUMENT = 8
    DOCUMENT_TYPE = 9
    NOTATION = 10

    def __init__(self, node, wrapper):
        if node is None or wrapper is None:
            raise Exception('Cannot instantiate without node and wrapper')
        self._impl_node = node
        self._wrapper = wrapper

    @property
    def impl_node(self):
        return self._impl_node

    @property
    def wrapper(self):
        return self._wrapper

    @property
    def impl_document(self):
        return self.wrapper.impl_document

    @property
    def root(self):
        # Return self if this is the root node
        if self.impl_node == self.wrapper.impl_root_element:
            return self
        return self.wrapper.wrap_impl_node(self.wrapper.impl_root_element)

    def is_type(self, node_type_constant):
        return self.node_type == node_type_constant

    @property
    def node_type(self):
        return self.wrapper.map_node_type(self.impl_node)

    def __eq__(self, other):
        if self is other:
            return True
        return self.impl_document == getattr(other, 'impl_document', None)

    def _convert_nodelist(self, nodelist):
        # TODO Do something more efficient here, lazy wrapping?
        return [self.wrapper.wrap_impl_node(n) for n in nodelist]

    @property
    def parent(self):
        # Root Element has no parent element
        if self.impl_node == self.wrapper.impl_root_element:
            return None
        return self.wrapper.wrap_impl_node(
            self.wrapper.get_node_parent(self.impl_node))

    def find(self, name=None, ns_uri=None, whole_document=False):
        if name is None:
            name = '*'  # Match all element names
        if ns_uri is None:
            ns_uri = '*'  # Match all namespaces
        if whole_document:
            search_from_node = self.impl_document
        else:
            search_from_node = self.impl_node
        nodelist = self.wrapper.find_node_elements(search_from_node,
            name=name, ns_uri=ns_uri)
        return self._convert_nodelist(nodelist)

    def doc_find(self, name=None, ns_uri=None):
        return self.find(name=name, ns_uri=ns_uri, whole_document=True)

    def find_first(self, name=None, ns_uri=None, whole_document=False):
        results = self.find(
            name=name, ns_uri=ns_uri, whole_document=whole_document)
        if results:
            return results[0]
        else:
            return None

    def _sanitize_write_value(self, value):
        if not value:
            return value
        return (value
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace("\"", "&quot;")
            .replace(">", "&gt;")
            )

    def _sanitize_write_params(self, indent='', newline=''):
        if isinstance(indent, int):
            indent = ' ' * indent
        elif indent is True:
            indent = ' ' * 4
        elif indent is False:
            indent = ''

        if newline is True:
            newline = '\n'
        elif newline is False:
            newline = ''

        return (indent, newline)

    # Methods that operate on this Node implementation wrapper

    def write(self, writer, encoding='utf-8',
            indent=0, newline='', quote_char='"', omit_declaration=False,
            _depth=0):
        raise NotImplementedError(
            'write is not implemented for %s' % self.__class__)

    def xml(self, encoding='utf-8',
            indent=4, newline='\n', quote_char='"', omit_declaration=False,
            _depth=0):
        writer = StringIO()
        if encoding is not None:
            codecs.getwriter(encoding)(writer)
        self.root.write(writer, encoding=encoding,
            indent=indent, newline=newline, quote_char=quote_char,
            omit_declaration=omit_declaration, _depth=_depth)
        return writer.getvalue()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.xml()


class _ValueNode(Node):

    def get_value(self):
        return self.wrapper.get_node_value(self.impl_node)

    def set_value(self, value):
        self.set_value(self.impl_node, value)

    value = property(get_value, set_value)

    def write(self, writer, encoding='utf-8',
            indent=0, newline='', quote_char='"', omit_declaration=False,
            _depth=0):
        indent, newline = self._sanitize_write_params(indent, newline)
        if self.is_type(Node.TEXT):
            writer.write(self._sanitize_write_value(self.value))
        elif self.is_type(Node.CDATA):
            if ']]>' in self.value:
                raise Exception("']]>' is not allowed in CDATA node value")
            writer.write("<![CDATA[%s]]>" % self.value)
        #elif self.is_type(Node.ENTITY): # TODO
        elif self.is_type(Node.COMMENT):
            if '--' in self.value:
                raise Exception("'--' is not allowed in COMMENT node value")
            writer.write("<!--%s-->" % self.value)
        #elif self.is_type(Node.NOTATION): # TODO
        else:
            raise Exception('write of node %s is not supported'
                % self.__class__)


class _NameValueNode(_ValueNode):

    def get_name(self):
        return self.wrapper.get_node_name(self.impl_node)

    def set_name(self, name):
        self.set_name(self.impl_node, name)

    name = property(get_name, set_name)


class Text(_ValueNode):
    pass


class CDATA(_ValueNode):
    pass


class Entity(_ValueNode):
    pass


class Comment(_ValueNode):
    pass


class Attribute(_NameValueNode):

    @property
    def prefix(self):
        if ':' in self.name:
            return self.name.split(':')[0]

    @property
    def local_name(self):
        if ':' in self.name:
            return self.name.split(':')[1]


class ProcessingInstruction(_NameValueNode):

    @property
    def target(self):
        return self.name

    @property
    def data(self):
        return self.value

    def write(self, writer, encoding='utf-8',
            indent=0, newline='', quote_char='"', omit_declaration=False,
            _depth=0):
        indent, newline = self._sanitize_write_params(indent, newline)
        writer.write(indent)
        writer.write("<?%s %s?>" % (self.target, self.data))
        writer.write(newline)


class Element(_NameValueNode):
    '''
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.
    '''

    @property
    def children(self, ns_uri=None):
        child_wrap_nodes = []
        for child in self.wrapper.get_node_children(
                self.impl_node, ns_uri=ns_uri):
            child_wrap_nodes.append(self.wrapper.wrap_impl_node(child))
        return child_wrap_nodes

    def up(self, count=1, to_tagname=None):
        elem = self.impl_node
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if (self.wrapper.get_node_parent(elem) is None
                or self.wrapper.get_node_parent(elem) == self.impl_document):

                return self.wrapper.wrap_impl_node(
                    self.wrapper.impl_root_element)
            elem = self.wrapper.get_node_parent(elem)
            if to_tagname is None:
                up_count += 1
                if up_count >= count:
                    break
            else:
                if self.wrapper.get_node_name(elem) == to_tagname:
                    break
        return self.wrapper.wrap_impl_node(elem)

    def build_element(self, tagname, ns_uri=None,
            attributes=None, text=None, before=False):
        elem = self.wrapper.new_impl_element(tagname, ns_uri)
        # Automatically add namespace URI to Element as attribute
        if ns_uri is not None:
            self._set_namespace(elem, ns_uri)
        if attributes is not None:
            self._set_attributes(elem, attr_obj=attributes)
        if text is not None:
            self._build_text(elem, text=text)
        if before:
            self.wrapper.add_node_child(
                self.wrapper.get_node_parent(self.impl_node),
                elem, before_sibling=self.impl_node)
        else:
            self.wrapper.add_node_child(self.impl_node, elem)
        return self.wrapper.wrap_impl_node(elem)

    build_elem = build_element  # Alias

    build_e = build_element  # Alias

    def _set_attributes(self, element,
            attr_obj=None, ns_uri=None, **attr_dict):
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
            self.wrapper.set_node_attribute(
                element, n, v, ns_uri=ns_uri)

    def get_attributes(self, ns_uri=None):
        attr_wrap_nodes = []
        for attr in self.wrapper.get_node_attributes(
                self.impl_node, ns_uri=ns_uri):
            attr_wrap_nodes.append(self.wrapper.wrap_impl_node(attr))
        return sorted(attr_wrap_nodes, key=lambda a: a.name)

    def set_attributes(self, attr_obj=None, ns_uri=None, **attr_dict):
        self._set_attributes(self.impl_node,
            attr_obj=attr_obj, ns_uri=ns_uri, **attr_dict)
        return self

    set_attrs = set_attributes  # Alias

    set_as = set_attributes  # Alias

    attributes = property(get_attributes, set_attributes)

    def _build_text(self, element, text):
        text_node = self.wrapper.new_impl_text(text)
        element.appendChild(text_node)

    def build_text(self, text):
        self._build_text(self.impl_node, text)
        return self

    build_t = build_text  # Alias

    # TODO set_text : replaces any existing text nodes

    def _build_comment(self, element, text):
        comment_node = self.wrapper.new_impl_comment(text)
        element.appendChild(comment_node)

    def build_comment(self, text):
        self._build_comment(self.impl_node, text)
        return self

    build_c = build_comment  # Alias

    def _build_instruction(self, element, target, data):
        instruction_node = self.wrapper.new_impl_instruction(target, data)
        element.appendChild(instruction_node)

    def build_instruction(self, target, data):
        self._build_instruction(self.impl_node, target, data)
        return self

    build_processing_instruction = build_instruction  # Alias

    build_i = build_instruction  # Alias

    def _set_namespace(self, element, ns_uri, prefix=None):
        if not prefix:
            ns_name = 'xmlns'
        else:
            ns_name = 'xmlns:%s' % prefix
        self._set_attributes(element,
            {ns_name: ns_uri},
            ns_uri=self.XMLNS_URI)

    def set_namespace(self, ns_uri, prefix=None):
        self._set_namespace(self.impl_node, ns_uri, prefix=prefix)
        return self

    set_ns = set_namespace  # Alias

    def _build_cdata(self, element, data):
        cdata_node = self.wrapper.new_impl_cdata(data)
        element.appendChild(cdata_node)

    def build_cdata(self, data):
        self._build_cdata(self.impl_node, data)
        return self

    build_data = build_cdata  # Alias

    build_d = build_cdata  # Alias

    # Adapted from standard library method xml.dom.minidom.writexml
    def write(self, writer, encoding='utf-8',
            indent=0, newline='', quote_char='"', omit_declaration=False,
            _depth=0):

        indent, newline = self._sanitize_write_params(indent, newline)

        # Output document declaration if we're outputting the whole doc
        if not omit_declaration and _depth < 1:
            writer.write('<?xml version="1.0"')
            if encoding:
                writer.write(' encoding="%s"' % encoding)
            writer.write('?>%s' % newline)

        writer.write(indent * _depth)
        writer.write("<" + self.name)

        for attr in self.attributes:
            writer.write(" %s=%s" % (attr.name, quote_char))
            # TODO Handle CDATA nodes (don't munge data)
            writer.write(self._sanitize_write_value(attr.value))
            writer.write(quote_char)
        if self.children:
            found_indented_child = False
            last_child_was_indented = False
            writer.write(">")
            for child in self.children:
                if (child.is_type(Node.ELEMENT)
                        or child.is_type(Node.PROCESSING_INSTRUCTION)):
                    if not last_child_was_indented:
                        writer.write(newline)
                    last_child_was_indented = True
                    found_indented_child = True
                else:
                    last_child_was_indented = False
                child.write(writer, encoding=encoding,
                    indent=indent, newline=newline, quote_char=quote_char,
                    omit_declaration=omit_declaration, _depth=_depth+1)
            if found_indented_child:
                writer.write(indent * _depth)
            writer.write('</%s>' % self.name)
        else:
            writer.write('/>')
        writer.write(newline)
