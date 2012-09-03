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

    def __unicode__(self):
        return u'<%s.%s>' % (
            self.__class__.__module__, self.__class__.__name__)

    def __str__(self):
        # TODO Degrade non-ASCII characters gracefully
        return str(self.__unicode__())

    def __repr__(self):
        return self.__str__()

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
        """Return the root Document of the document containing this node"""
        if self.is_document:
            return self
        return self.adapter.wrap_document(self.adapter.impl_document)

    @property
    def root(self):
        if self.is_root:
            return self
        return self.adapter.wrap_node(
            self.adapter.impl_root_element, self.adapter.impl_document)

    @property
    def is_root(self):
        return self.impl_node == self.adapter.impl_root_element

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
        return [self.adapter.wrap_node(n, self.adapter.impl_document)
                for n in nodelist]

    @property
    def parent(self):
        parent_impl_node = self.adapter.get_node_parent(self.impl_node)
        return self.adapter.wrap_node(
            parent_impl_node, self.adapter.impl_document)

    @property
    def ancestors(self):
        """
        Return the ancestors of this node in an ordered list with this node's
        parent, grand-parent, great-grand-parent etc.
        """
        ancestors = []
        p = self.parent
        while p:
            ancestors.append(p)
            p = p.parent
        return ancestors

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

    @property
    def attributes(self):
        return None

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
        return self.adapter.get_node_namespace_uri(self.impl_node)

    ns_uri = namespace_uri  # Alias

    @property
    def current_namespace_uri(self):
        curr_node = self
        while curr_node:
            if curr_node.namespace_uri is not None:
                return self.namespace_uri
            curr_node = curr_node.parent
        return None

    def delete(self):
        self.adapter.remove_node_child(
            self.adapter.get_node_parent(self.impl_node), self.impl_node,
            destroy_node=True)

    def find(self, name=None, ns_uri=None, first_only=False):
        """
        Return a list of Element node descendents of this node that match
        the given constraints.
        """
        if name is None:
            name = '*'  # Match all element names
        if ns_uri is None:
            ns_uri = '*'  # Match all namespaces
        nodelist = self.adapter.find_node_elements(
            self.impl_node, name=name, ns_uri=ns_uri)
        if first_only:
            if nodelist:
                return self.adapter.wrap_node(
                    nodelist[0], self.adapter.impl_document)
            else:
                return None
        return self._convert_nodelist(nodelist)

    def find_first(self, name=None, ns_uri=None):
        return self.find(name=name, ns_uri=ns_uri, first_only=True)

    def doc_find(self, name=None, ns_uri=None, first_only=False):
        """
        Return a list of all Element nodes in the document that match
        the given constraints.
        """
        return self.document.find(name=name, ns_uri=ns_uri,
            first_only=first_only)

    # Methods that operate on this Node implementation adapter

    def write(self, writer, encoding='utf-8', indent=False, newline=False,
            quote_char='"', omit_declaration=False, _depth=0):
        write_func(self, writer, encoding=encoding,
            indent=indent, newline=newline, quote_char=quote_char,
            omit_declaration=omit_declaration, _depth=_depth)

    def doc_write(self, writer, encoding='utf-8', indent=False, newline=False,
            quote_char='"', omit_declaration=False, _depth=0):
        self.document.write(writer, encoding=encoding,
            indent=indent, newline=newline, quote_char=quote_char,
            omit_declaration=omit_declaration, _depth=_depth)

    def xml(self, encoding='utf-8', indent=4, newline='\n',
            quote_char='"', omit_declaration=False, _depth=0):
        """
        Return XML document as a string
        """
        writer = StringIO()
        if encoding is not None:
            codecs.getwriter(encoding)(writer)
        self.write(writer, encoding=encoding,
            indent=indent, newline=newline, quote_char=quote_char,
            omit_declaration=omit_declaration, _depth=_depth)
        return writer.getvalue()

    def doc_xml(self, encoding='utf-8', indent=4, newline='\n',
            quote_char='"', omit_declaration=False, _depth=0):
        return self.document.xml(encoding=encoding,
            indent=indent, newline=newline, quote_char=quote_char,
            omit_declaration=omit_declaration, _depth=_depth)


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

    def __unicode__(self):
        return u'<%s.%s: "%s">' % (
            self.__class__.__module__, self.__class__.__name__,
            self.name)

    @property
    def prefix(self):
        return self.adapter.get_node_name_prefix(self.impl_node)

    @property
    def local_name(self):
        return self.adapter.get_node_local_name(self.impl_node)

    @property
    def name(self):
        return self.adapter.get_node_name(self.impl_node)

    @name.setter
    def name(self, name):
        self.set_name(self.impl_node, name)

    @property
    def value(self):
        return self.adapter.get_node_value(self.impl_node)

    @value.setter
    def value(self, value):
        self.adapter.set_node_value(self.impl_node, value)


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
        return super(Attribute, self).name

    # Cannot set/change value of attribute
    @property
    def value(self):
        return super(Attribute, self).value


class ProcessingInstruction(_NameValueNode):
    _node_type = PROCESSING_INSTRUCTION_NODE

    target = _NameValueNode.name

    data = _NameValueNode.value


class Element(_NameValueNode):
    """
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.
    """
    _node_type = ELEMENT_NODE

    @property
    def text(self):
        return self.adapter.get_node_text(self.impl_node)

    @text.setter
    def text(self, text):
        self.adapter.set_node_text(self.impl_node, text)

    def attributes_by_ns(self, ns_uri):
        attr_impl_nodes = self.adapter.get_node_attributes(
            self.impl_node, ns_uri=ns_uri)
        return AttributeDict(attr_impl_nodes, self.impl_node, self.adapter)

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

        # Always process 'xmlns' namespace definitions first, in case other
        # attributes belong to a newly-defined namespace
        def _xmlns_first(x, y):
            nx, ny = x[0], y[0]
            if nx.startswith('xmlns') and ny.startswith('xmlns'):
                return cmp(nx, ny)
            elif nx.startswith('xmlns'):
                return -1
            elif ny.startswith('xmlns'):
                return 1
            else:
                return cmp(nx, ny)
        attr_list = sorted(attr_dict.items(), cmp=_xmlns_first)
        # Add attributes
        for attr_name, v in attr_list:
            prefix, name, my_ns_uri = self.adapter.get_ns_info_from_node_name(
                attr_name, element)
            if ' ' in name:
                raise Exception("Invalid attribute name value contains space")
            # If necessary, add an xmlns defn for new prefix-defined namespace
            if not prefix and '}' in attr_name:
                prefix = self.adapter.get_ns_prefix_for_uri(
                    element, my_ns_uri, auto_generate_prefix=True)
                self.adapter.set_node_attribute_value(element,
                    'xmlns:%s' % prefix, my_ns_uri, ns_uri=self.XMLNS_URI)
            # Apply kw-specified namespace if not overridden by prefix name
            if my_ns_uri is None:
                my_ns_uri = ns_uri
            if ns_uri is not None:
                # Apply attribute namespace URI if different from owning elem
                if ns_uri == self.adapter.get_node_namespace_uri(element):
                    my_ns_uri = None
            # Forcibly convert all data to unicode text
            if not isinstance(v, basestring):
                v = unicode(v)
            if prefix:
                qname = '%s:%s' % (prefix, name)
            else:
                qname = name
            self.adapter.set_node_attribute_value(
                element, qname, v, ns_uri=my_ns_uri)

    def set_attributes(self, attr_obj=None, ns_uri=None, **attr_dict):
        self._set_element_attributes(self.impl_node,
            attr_obj=attr_obj, ns_uri=ns_uri, **attr_dict)

    @property
    def attributes(self):
        return self.attributes_by_ns(None)

    @attributes.setter
    def attributes(self, attr_obj=None, ns_uri=None, **attr_dict):
        # Remove existing attributes
        for attr_name in self.attributes:
            self.adapter.remove_node_attribute(
                self.impl_node, attr_name, ns_uri)
        # Add new attributes
        self._set_element_attributes(self.impl_node,
            attr_obj=attr_obj, ns_uri=ns_uri, **attr_dict)

    @property
    def attribute_nodes(self):
        impl_attr_nodes = self.adapter.get_node_attributes(self.impl_node)
        wrapped_attr_nodes = [
            self.adapter.wrap_node(a, self.adapter.impl_document)
            for a in impl_attr_nodes]
        return sorted(wrapped_attr_nodes, key=lambda x: x.name)

    def attribute_node(self, name, ns_uri=None):
        attr_impl_node = self.adapter.get_node_attribute_node(
            self.impl_node, name, ns_uri)
        return self.adapter.wrap_node(
            attr_impl_node, self.adapter.impl_document)

    def _add_ns_prefix_attr(self, element, prefix, ns_uri):
        if prefix is None:
            ns_name = 'xmlns'
            self.adapter.set_node_namespace_uri(element, ns_uri)
        else:
            ns_name = 'xmlns:%s' % prefix
        self._set_element_attributes(element,
            {ns_name: ns_uri}, ns_uri=self.XMLNS_URI)

    def set_ns_prefix(self, prefix, ns_uri):
        self._add_ns_prefix_attr(self.impl_node, prefix, ns_uri)

    def add_element(self, tagname, ns_uri=None, prefix=None,
            attributes=None, text=None, before_this_element=False):
        # Determine local name, namespace and prefix info from tag name
        prefix, name, node_ns_uri = self.adapter.get_ns_info_from_node_name(
            tagname, self.impl_node)
        if prefix:
            qname = '%s:%s' % (prefix, name)
        else:
            qname = name
        # If no name-derived namespace, apply an alternate namespace
        if node_ns_uri is None:
            if ns_uri is None:
                # Default document namespace
                node_ns_uri = self.adapter.get_ns_uri_for_prefix(
                    self.impl_node, None)
            else:
                # keyword-parameter namespace
                node_ns_uri = ns_uri
        # Create element
        child_elem = self.adapter.new_impl_element(
            qname, node_ns_uri, parent=self.impl_node)
        # If element's default namespace was defined by literal uri prefix,
        # create corresponding xmlns attribute for element...
        if not prefix and '}' in tagname:
            self._set_element_attributes(child_elem,
                {'xmlns': node_ns_uri}, ns_uri=self.XMLNS_URI)
        # ...otherwise define keyword-defined namespace as the default, if any
        elif ns_uri is not None:
            self._set_element_attributes(child_elem,
                {'xmlns': ns_uri}, ns_uri=self.XMLNS_URI)
        # Create subordinate nodes
        if attributes is not None:
            self._set_element_attributes(child_elem, attr_obj=attributes)
        if text is not None:
            self._add_text(child_elem, text)
        # Add new element to its parent before a given node...
        if before_this_element:
            self.adapter.add_node_child(
                self.adapter.get_node_parent(self.impl_node),
                child_elem, before_sibling=self.impl_node)
        # ...or in the default position, appended after existing nodes
        else:
            self.adapter.add_node_child(self.impl_node, child_elem)
        return self.adapter.wrap_node(child_elem, self.adapter.impl_document)

    def _add_text(self, element, text):
        text_node = self.adapter.new_impl_text(text)
        self.adapter.add_node_child(element, text_node)

    def add_text(self, text):
        self._add_text(self.impl_node, text)

    def _add_comment(self, element, text):
        comment_node = self.adapter.new_impl_comment(text)
        self.adapter.add_node_child(element, comment_node)

    def add_comment(self, text):
        self._add_comment(self.impl_node, text)

    def _add_instruction(self, element, target, data):
        instruction_node = self.adapter.new_impl_instruction(target, data)
        self.adapter.add_node_child(element, instruction_node)

    def add_instruction(self, target, data):
        self._add_instruction(self.impl_node, target, data)

    def _add_cdata(self, element, data):
        cdata_node = self.adapter.new_impl_cdata(data)
        self.adapter.add_node_child(element, cdata_node)

    def add_cdata(self, data):
        self._add_cdata(self.impl_node, data)


class AttributeDict(object):
    """
    Dictionary-like object of element attributes that always reflects the
    state of the underlying element node, and that allows for in-place
    modifications that will immediately affect the element.
    """

    def __init__(self, attr_impl_nodes, impl_element, adapter):
        self.impl_element = impl_element
        self.adapter = adapter

    def __len__(self):
        return len(self.impl_attributes)

    def __getitem__(self, attr_name):
        prefix, name, ns_uri = self.adapter.get_ns_info_from_node_name(
            attr_name, self.impl_element)
        return self.adapter.get_node_attribute_value(
            self.impl_element, name, ns_uri)

    def __setitem__(self, name, value):
        prefix, name, ns_uri = self.adapter.get_ns_info_from_node_name(
            name, self.impl_element)
        if not isinstance(value, basestring):
            value = unicode(value)
        self.adapter.set_node_attribute_value(
            self.impl_element, name, value, ns_uri)

    def __delitem__(self, name):
        prefix, name, ns_uri = self.adapter.get_ns_info_from_node_name(
            name, self.impl_element)
        self.adapter.remove_node_attribute(self.impl_element, name, ns_uri)

    def __iter__(self):
        for k in self.keys():
            yield k

    iterkeys = __iter__  # Alias, per Python docs recommendation

    def __contains__(self, name):
        prefix, name, ns_uri = self.adapter.get_ns_info_from_node_name(
            name, self.impl_element)
        return self.adapter.has_node_attribute(self.impl_element, name, ns_uri)

    def keys(self):
        return [self.adapter.get_node_name(a) for a in self.impl_attributes]

    def values(self):
        return [self.adapter.get_node_value(a) for a in self.impl_attributes]

    def namespace_uri(self, name):
        a_node = self.adapter.get_node_attribute_node(self.impl_element, name)
        if a_node is None:
            return None
        return self.adapter.get_node_namespace_uri(a_node)

    def prefix(self, name):
        a_node = self.adapter.get_node_attribute_node(self.impl_element, name)
        if a_node is None:
            return None
        return a_node.prefix

    @property
    def element(self):
        return self.adapter.wrap_node(
            self.impl_element, self.adapter.impl_document)

    @property
    def impl_attributes(self):
        return self.adapter.get_node_attributes(self.impl_element)
