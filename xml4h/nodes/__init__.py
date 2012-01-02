import codecs
from StringIO import StringIO

import xml4h.writer


class Node(object):
    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    CDATA_SECTION_NODE = 4
    ENTITY_NODE = 5
    PROCESSING_INSTRUCTION_NODE = 6
    COMMENT_NODE = 7
    DOCUMENT_NODE = 8
    DOCUMENT_TYPE_NODE = 9
    NOTATION_NODE = 10

    def __init__(self, node, document):
        if document is None or node is None:
            raise Exception('Cannot instantiate without node and document')
        self._node = node
        self._document = document

    @property
    def root(self):
        return self._wrap_impl_node(
            self._get_root_element(), self.impl_document)

    @property
    def impl_node(self):
        return self._node

    @property
    def impl_document(self):
        return self._document

    def is_type(self, node_type_constant):
        return self.node_type == node_type_constant

    @property
    def node_type(self):
        return self._map_node_type(self.impl_node)

    def __eq__(self, other):
        if self is other:
            return True
        return self.impl_document == getattr(other, 'impl_document', None)

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


    # Methods that operate on underlying DOM implementation

    @classmethod
    def _wrap_impl_node(self, impl_node, impl_document):
        raise NotImplementedError()

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

    def _get_parent(self, node):
        raise NotImplementedError()

    def _get_children(self, node, namespace_uri=None):
        raise NotImplementedError()

    def _map_node_type(self, node):
        raise NotImplementedError()

    def _get_root_element(self):
        raise NotImplementedError()



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


class ValueNode(Node):

    def _get_value(self, node):
        raise NotImplementedError()

    def _set_value(self, node, value):
        raise NotImplementedError()


    def get_value(self):
        return self._get_value(self.impl_node)

    def set_value(self, value):
        self._set_value(self.impl_node, value)

    value = property(get_value, set_value)

    def write(self, writer, encoding='utf-8',
            indent=0, newline='', quote_char='"', omit_declaration=False,
            _depth=0):
        indent, newline = self._sanitize_write_params(indent, newline)
        if self.is_type(Node.TEXT_NODE):
            writer.write(self._sanitize_write_value(self.value))
        elif self.is_type(Node.CDATA_SECTION_NODE):
            if ']]>' in self.value:
                raise Exception("']]>' is not allowed in CDATA node value")
            writer.write("<![CDATA[%s]]>" % self.value)
        #elif self.is_type(Node.ENTITY_NODE): # TODO
        elif self.is_type(Node.COMMENT_NODE):
            if '--' in self.value:
                raise Exception("'--' is not allowed in COMMENT node value")
            writer.write("<!--%s-->" % self.value)
        #elif self.is_type(Node.NOTATION_NODE): # TODO
        else:
            raise Exception('write of node %s is not supported'
                % self.__class__)


class NameValueNode(ValueNode):

    def _get_name(self, node):
        raise NotImplementedError()

    def _set_name(self, node, name):
        raise NotImplementedError()

    def get_name(self):
        return self._get_name(self.impl_node)

    def set_name(self, name):
        self._set_name(self.impl_node, name)

    name = property(get_name, set_name)


class AttributeNode(NameValueNode):

    @property
    def prefix(self):
        if ':' in self.name:
            return self.name.split(':')[0]

    @property
    def local_name(self):
        if ':' in self.name:
            return self.name.split(':')[1]


class ProcessingInstructionNode(NameValueNode):

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


class ElementNode(NameValueNode):
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

    def _get_attributes(self, element, namespace_uri=None):
        raise NotImplementedError()


    @property
    def children(self, namespace_uri=None):
        child_wrap_nodes = []
        for child in self._get_children(
                self.impl_node, namespace_uri=namespace_uri):
            child_wrap_nodes.append(
                self._wrap_impl_node(child, self.impl_document))
        return child_wrap_nodes

    def up(self, count=1, to_tagname=None):
        elem = self.impl_node
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if (self._get_parent(elem) is None
                    or self._get_parent(elem) == self.impl_document):
                return self._wrap_impl_node(self._get_root_element(), self.impl_document)
            elem = self._get_parent(elem)
            if to_tagname is None:
                up_count += 1
                if up_count >= count:
                    break
            else:
                if self._get_name(elem) == to_tagname:
                    break
        return self._wrap_impl_node(elem, self.impl_document)

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
                self._get_parent(self.impl_node), elem,
                before_sibling=self.impl_node)
        else:
            self._add_child_node(self.impl_node, elem)
        return self._wrap_impl_node(elem, self.impl_document)

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

    def get_attributes(self, namespace_uri=None):
        attr_wrap_nodes = []
        for attr in self._get_attributes(
                self.impl_node, namespace_uri=namespace_uri):
            attr_wrap_nodes.append(
                self._wrap_impl_node(attr, self.impl_document))
        return sorted(attr_wrap_nodes, key=lambda a: a.name)

    def set_attributes(self, attr_obj=None, namespace_uri=None, **attr_dict):
        self._set_attributes(self.impl_node,
            attr_obj=attr_obj, namespace_uri=namespace_uri, **attr_dict)
        return self

    set_attrs = set_attributes  # Alias

    set_as = set_attributes  # Alias

    attributes = property(get_attributes, set_attributes)

    def _add_text(self, element, text):
        text_node = self._new_text_node(text)
        element.appendChild(text_node)

    def add_text(self, text):
        self._add_text(self.impl_node, text)
        return self

    add_t = add_text  # Alias

    # TODO set_text : replaces any existing text nodes

    def _add_comment(self, element, text):
        comment_node = self._new_comment_node(text)
        element.appendChild(comment_node)

    def add_comment(self, text):
        self._add_comment(self.impl_node, text)
        return self

    add_c = add_comment  # Alias

    def _add_instruction(self, element, target, data):
        instruction_node = self._new_processing_instruction_node(target, data)
        element.appendChild(instruction_node)

    def add_instruction(self, target, data):
        self._add_instruction(self.impl_node, target, data)
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
        self._set_namespace(self.impl_node, namespace_uri, prefix=prefix)
        return self

    set_ns = set_namespace  # Alias

    def _add_cdata(self, element, data):
        cdata_node = self._new_cdata_node(data)
        element.appendChild(cdata_node)

    def add_cdata(self, data):
        self._add_cdata(self.impl_node, data)
        return self

    add_data = add_cdata  # Alias

    add_d = add_cdata  # Alias

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
                if (child.is_type(Node.ELEMENT_NODE)
                        or child.is_type(Node.PROCESSING_INSTRUCTION_NODE)):
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
