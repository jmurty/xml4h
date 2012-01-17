import codecs
from StringIO import StringIO

from xml4h.writer import write as write_func


ELEMENT_NODE = 1
ATTRIBUTE_NODE = 2
TEXT_NODE = 3
CDATA_NODE = 4
ENTITY_REFERENCE_NODE = 5
ENTITY_NODE = 6
PROCESSING_INSTRUCTION_NODE = 7
COMMENT_NODE = 8
DOCUMENT_NODE = 9
DOCUMENT_TYPE_NODE = 10
DOCUMENT_FRAGMENT_NODE = 11
NOTATION_NODE = 12


class Node(object):
    XMLNS_URI = 'http://www.w3.org/2000/xmlns/'

    def __init__(self, node, adapter):
        if node is None or adapter is None:
            raise Exception('Cannot instantiate without node and adapter')
        self._impl_node = node
        self._adapter = adapter

    @property
    def impl_node(self):
        return self._impl_node

    @property
    def adapter(self):
        return self._adapter

    @property
    def impl_document(self):
        return self.adapter.impl_document

    @property
    def document(self):
        # Return self if this is the document node
        if self.impl_node == self.adapter.impl_document:
            return self
        return self.adapter.wrap_node(self.adapter.impl_document)

    @property
    def root(self):
        # Return self if this is the root element node
        if self.impl_node == self.adapter.impl_root_element:
            return self
        return self.adapter.wrap_node(self.adapter.impl_root_element)

    @property
    def node_type(self):
        return self._node_type

    def is_type(self, node_type_constant):
        return self.node_type == node_type_constant

    @property
    def is_element(self):
        return self.is_type(ELEMENT_NODE)

    @property
    def is_attribute(self):
        return self.is_type(ATTRIBUTE_NODE)

    @property
    def is_text(self):
        return self.is_type(TEXT_NODE)

    @property
    def is_cdata(self):
        return self.is_type(CDATA_NODE)

    @property
    def is_entity_reference(self):
        return self.is_type(ENTITY_REFERENCE_NODE)

    @property
    def is_entity(self):
        return self.is_type(ENTITY_NODE)

    @property
    def is_processing_instruction(self):
        return self.is_type(PROCESSING_INSTRUCTION_NODE)

    @property
    def is_comment(self):
        return self.is_type(COMMENT_NODE)

    @property
    def is_document(self):
        return self.is_type(DOCUMENT_NODE)

    @property
    def is_document_type(self):
        return self.is_type(DOCUMENT_TYPE_NODE)

    @property
    def is_document_fragment(self):
        return self.is_type(DOCUMENT_FRAGMENT_NODE)

    @property
    def is_notation(self):
        return self.is_type(NOTATION_NODE)

    def __eq__(self, other):
        if self is other:
            return True
        return self.impl_document == getattr(other, 'impl_document', None)

    def _convert_nodelist(self, nodelist):
        # TODO Do something more efficient here, lazy wrapping?
        return [self.adapter.wrap_node(n) for n in nodelist]

    @property
    def parent(self):
        parent_impl_node = self.adapter.get_node_parent(self.impl_node)
        if parent_impl_node is not None:
            return self.adapter.wrap_node(parent_impl_node)
        else:
            return None

    def children_in_ns(self, ns_uri):
        nodelist = self.adapter.get_node_children(self.impl_node)
        if ns_uri is not None:
            nodelist = filter(
                lambda x: self.adapter.get_node_namespace_uri(x) == ns_uri,
                nodelist)
        return self._convert_nodelist(nodelist)

    @property
    def children(self):
        return self.children_in_ns(None)

    # TODO: Better to leave this undefined?
    @property
    def attributes(self):
        return None

    # TODO: Better to leave this undefined?
    @property
    def attribute_nodes(self):
        return None

    def siblings_in_ns(self, ns_uri):
        nodelist = self.adapter.get_node_children(self.parent.impl_node)
        return self._convert_nodelist(
            [n for n in nodelist if n != self.impl_node])

    @property
    def siblings(self):
        return self.siblings_in_ns(None)

    @property
    def siblings_before(self):
        nodelist = self.adapter.get_node_children(self.parent.impl_node)
        before_nodelist = []
        for n in nodelist:
            if n == self.impl_node:
                break
            before_nodelist.append(n)
        return self._convert_nodelist(before_nodelist)

    @property
    def siblings_after(self):
        nodelist = self.adapter.get_node_children(self.parent.impl_node)
        after_nodelist = []
        is_after_myself = False
        for n in nodelist:
            if is_after_myself:
                after_nodelist.append(n)
            elif n == self.impl_node:
                is_after_myself = True
        return self._convert_nodelist(after_nodelist)

    @property
    def namespace_uri(self):
        return self.impl_node.namespaceURI

    ns_uri = namespace_uri  # Alias

    @property
    def prefix(self):
        return self.impl_node.prefix

    @property
    def local_name(self):
        return self.impl_node.localName

    def delete(self):
        self.adapter.remove_node_child(
            self.adapter.get_node_parent(self.impl_node), self.impl_node,
            destroy_node=True)

    def find(self, name=None, ns_uri=None, whole_document=False):
        if name is None:
            name = '*'  # Match all element names
        if ns_uri is None:
            ns_uri = '*'  # Match all namespaces
        if whole_document:
            search_from_node = self.impl_document
        else:
            search_from_node = self.impl_node
        nodelist = self.adapter.find_node_elements(search_from_node,
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

    # Methods that operate on this Node implementation adapter

    def write(self, writer, **kwargs):
        write_func(self.document, writer, **kwargs)

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


class Document(Node):
    _node_type = DOCUMENT_NODE
    # TODO: doc_type, document_element


class DocumentType(Node):
    _node_type = DOCUMENT_TYPE_NODE
    # TODO: name, entities, notations, public_id, system_id


class DocumentFragment(Node):
    _node_type = DOCUMENT_FRAGMENT_NODE
    # TODO


class Notation(Node):
    _node_type = NOTATION_NODE
    # TODO: public_id, system_id


class Entity(Node):
    _node_type = ENTITY_NODE
    # public_id, system_id

    @property
    def notation_name(self):
        return self.name


class EntityReference(Node):
    _node_type = ENTITY_REFERENCE_NODE
    # TODO


class _NameValueNode(Node):

    def _get_name(self):
        return self.adapter.get_node_name(self.impl_node)

    def _set_name(self, name):
        self.set_name(self.impl_node, name)

    name = property(_get_name, _set_name)

    def _get_value(self):
        return self.adapter.get_node_value(self.impl_node)

    def _set_value(self, value):
        self.adapter.set_node_value(self.impl_node, value)

    value = property(_get_value, _set_value)


class Text(_NameValueNode):
    _node_type = TEXT_NODE


class CDATA(_NameValueNode):
    _node_type = CDATA_NODE


class Entity(_NameValueNode):
    _node_type = ENTITY_NODE


class Comment(_NameValueNode):
    _node_type = COMMENT_NODE


class Attribute(_NameValueNode):
    _node_type = ATTRIBUTE_NODE

    # Cannot set/change name of attribute
    @property
    def name(self):
        return self._get_name()

    # Cannot set/change value of attribute
    @property
    def value(self):
        return self._get_value()

    @property
    def prefix(self):
        if ':' in self.name:
            return self.name.split(':')[0]
        else:
            return None

    @property
    def local_name(self):
        if ':' in self.name:
            return self.name.split(':')[1]
        else:
            return self.name


class ProcessingInstruction(_NameValueNode):
    _node_type = PROCESSING_INSTRUCTION_NODE

    @property
    def target(self):
        return self.name

    @property
    def data(self):
        return self.value


class Element(_NameValueNode):
    '''
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.
    '''
    _node_type = ELEMENT_NODE

    def _get_text(self):
        '''
        Return contatenated value of all text node children of this element
        '''
        # TODO Make this more efficient
        text_children = [n.value for n in self.children if n.is_text]
        if text_children:
            return u''.join(text_children)
        else:
            return None

    def _set_text(self, text):
        '''
        Set text value as sole Text child node of element; any existing
        Text nodes are removed
        '''
        # Remove any existing Text node children
        for child in self.children:
            if child.is_text:
                child.delete()
        if text is not None:
            text_node = self.adapter.new_impl_text(text)
            self.adapter.add_node_child(self.impl_node, text_node)

    text = property(_get_text, _set_text)

    def _get_attributes(self, ns_uri=None):
        attr_impl_nodes = self.adapter.get_node_attributes(
            self.impl_node, ns_uri=ns_uri)
        return AttributeDict(attr_impl_nodes, self.impl_node, self.adapter)

    def _set_attributes(self, attr_obj=None, ns_uri=None, **attr_dict):
        # Remove existing attributes
        for attr_name in self._get_attributes(ns_uri):
            self.adapter.remove_node_attribute(
                self.impl_node, attr_name, ns_uri)
        # Add new attributes
        self._set_element_attributes(self.impl_node,
            attr_obj=attr_obj, ns_uri=ns_uri, **attr_dict)

    attributes = property(_get_attributes, _set_attributes)

    @property
    def attribute_nodes(self):
        impl_attr_nodes = self.adapter.get_node_attributes(self.impl_node)
        wrapped_attr_nodes = [self.adapter.wrap_node(a, self.impl_document)
                              for a in impl_attr_nodes]
        return sorted(wrapped_attr_nodes, key=lambda x: x.name)

    def attribute_node(self, name, ns_uri=None):
        attr_impl_node = self.adapter.get_node_attribute_node(
            self.impl_node, name, ns_uri)
        return self.adapter.wrap_node(attr_impl_node, self.impl_document)

    def up(self, count=1, to_tagname=None):
        elem = self.impl_node
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if (self.adapter.get_node_parent(elem) is None
                or self.adapter.get_node_parent(elem) == self.impl_document):

                return self.adapter.wrap_node(
                    self.adapter.impl_root_element)
            elem = self.adapter.get_node_parent(elem)
            if to_tagname is None:
                up_count += 1
                if up_count >= count:
                    break
            else:
                if self.adapter.get_node_name(elem) == to_tagname:
                    break
        return self.adapter.wrap_node(elem)

    def build_element(self, tagname, ns_uri=None, prefix=None,
            attributes=None, text=None, before=False):
        if prefix is not None:
            tagname = '%s:%s' % (prefix, tagname)
        elem = self.adapter.new_impl_element(tagname, ns_uri)
        # Automatically add namespace URI to Element as attribute
        if ns_uri is not None:
            self._set_namespace(elem, ns_uri)
        if attributes is not None:
            self._set_element_attributes(elem, attr_obj=attributes)
        if text is not None:
            self._build_text(elem, text)
        if before:
            self.adapter.add_node_child(
                self.adapter.get_node_parent(self.impl_node),
                elem, before_sibling=self.impl_node)
        else:
            self.adapter.add_node_child(self.impl_node, elem)
        return self.adapter.wrap_node(elem)

    build_elem = build_element  # Alias

    build_e = build_element  # Alias

    def _set_element_attributes(self, element,
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
            my_ns_uri = ns_uri
            if isinstance(n, tuple):
                n, my_ns_uri = n
            if ' ' in n:
                raise Exception("Invalid attribute name value contains space")
            # TODO Necessary? Desirable?
            if not isinstance(v, basestring):
                v = unicode(v)
            self.adapter.set_node_attribute_value(
                element, n, v, ns_uri=my_ns_uri)

    def set_attributes(self, attr_obj=None, ns_uri=None, **attr_dict):
        self._set_element_attributes(self.impl_node,
            attr_obj=attr_obj, ns_uri=ns_uri, **attr_dict)

    def build_attributes(self, attr_obj=None, ns_uri=None, **attr_dict):
        self._set_element_attributes(self.impl_node,
            attr_obj=attr_obj, ns_uri=ns_uri, **attr_dict)
        return self

    build_attrs = build_attributes  # Alias

    build_as = build_attributes  # Alias

    def _build_text(self, element, text):
        text_node = self.adapter.new_impl_text(text)
        self.adapter.add_node_child(element, text_node)

    def build_text(self, text):
        self._build_text(self.impl_node, text)
        return self

    build_t = build_text  # Alias

    # TODO set_text : replaces any existing text nodes

    def _build_comment(self, element, text):
        comment_node = self.adapter.new_impl_comment(text)
        self.adapter.add_node_child(element, comment_node)

    def build_comment(self, text):
        self._build_comment(self.impl_node, text)
        return self

    build_c = build_comment  # Alias

    def _build_instruction(self, element, target, data):
        instruction_node = self.adapter.new_impl_instruction(target, data)
        self.adapter.add_node_child(element, instruction_node)

    def build_instruction(self, target, data):
        self._build_instruction(self.impl_node, target, data)
        return self

    build_processing_instruction = build_instruction  # Alias

    build_i = build_instruction  # Alias

    def _set_namespace(self, element, ns_uri, prefix=None):
        if not prefix:
            # Apply default namespace to node
            self.adapter.set_node_namespace_uri(element, ns_uri)
            ns_name = 'xmlns'
        else:
            ns_name = 'xmlns:%s' % prefix
        self._set_element_attributes(element,
            {ns_name: ns_uri},
            ns_uri=self.XMLNS_URI)

    def set_namespace(self, ns_uri, prefix=None):
        self._set_namespace(self.impl_node, ns_uri, prefix=prefix)
        return self

    set_ns = set_namespace  # Alias

    def _build_cdata(self, element, data):
        cdata_node = self.adapter.new_impl_cdata(data)
        self.adapter.add_node_child(element, cdata_node)

    def build_cdata(self, data):
        self._build_cdata(self.impl_node, data)
        return self

    build_data = build_cdata  # Alias

    build_d = build_cdata  # Alias


class AttributeDict(object):
    '''
    Dictionary-like object of element attributes that always reflects the
    state of the underlying element node, and that allows for in-place
    modifications that will immediately affect the element.
    '''

    def __init__(self, attr_impl_nodes, impl_element, adapter):
        self.impl_element = impl_element
        self.adapter = adapter

    def _unpack_name(self, name):
        if isinstance(name, tuple):
            name, ns_uri = name
            return name, ns_uri
        else:
            return name, None

    def __len__(self):
        return len(self.impl_attributes)

    def __getitem__(self, name):
        name, ns_uri = self._unpack_name(name)
        # Override behavior of some (all?) implementations that return an
        # empty string if attribute does not exist
        if not name in self:
            return None
        return self.adapter.get_node_attribute_value(
            self.impl_element, name, ns_uri)

    def __setitem__(self, name, value):
        name, ns_uri = self._unpack_name(name)
        if not isinstance(value, basestring):
            value = unicode(value)
        self.adapter.set_node_attribute_value(
            self.impl_element, name, value, ns_uri)

    def __delitem__(self, name):
        name, ns_uri = self._unpack_name(name)
        self.adapter.remove_node_attribute(self.impl_element, name, ns_uri)

    def __iter__(self):
        for k in self.keys():
            yield k

    iterkeys = __iter__  # Alias, per Python docs recommendation

    def __contains__(self, name):
        name, ns_uri = self._unpack_name(name)
        return self.adapter.has_node_attribute(self.impl_element, name, ns_uri)

    def keys(self):
        return [self.adapter.get_node_name(a) for a in self.impl_attributes]

    def values(self):
        return [self.adapter.get_node_value(a) for a in self.impl_attributes]

    def namespace_uri(self, name):
        a_node = self.adapter.get_node_attribute_node(self.impl_element, name)
        if a_node is None:
            return None
        return a_node.namespaceURI

    @property
    def element(self):
        return self.adapter.wrap_node(self.impl_element)

    @property
    def impl_attributes(self):
        return self.adapter.get_node_attributes(self.impl_element)

