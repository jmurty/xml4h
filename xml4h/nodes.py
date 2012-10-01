import collections
from StringIO import StringIO

import xml4h


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
    """
    Base class for *xml4h* DOM nodes that represent and interact with a
    node in the underlying XML implementation.
    """

    XMLNS_URI = 'http://www.w3.org/2000/xmlns/'
    """URI constant for XMLNS"""

    def __init__(self, node, adapter):
        """
        Construct an object that represents and wraps a DOM node in the
        underlying XML implementation.

        :param node: node object from the underlying XML implementation.
        :param adapter: the :class:`xml4h.impls._XmlImplAdapter`
            subclass implementation to mediate operations on the node in
            the underlying XML implementation.
        """
        if node is None or adapter is None:
            raise Exception('Cannot instantiate without node and adapter')
        self._impl_node = node
        self._adapter = adapter

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, Node):
            return False
        return (self.impl_document == other.impl_document
            and self.impl_node == other.impl_node)

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
        """
        :return: the node object from the underlying XML implementation that
            is represented by this *xml4h* node.
        """
        return self._impl_node

    @property
    def impl_document(self):
        """
        :return: the document object from the underlying XML implementation
            that contains the node represented by this *xml4h* node.
        """
        return self.adapter.impl_document

    @property
    def adapter(self):
        """
        :return: the :class:`xml4h.impls._XmlImplAdapter` subclass
            implementation that mediates operations on the node in the
            underlying XML implementation.
        """
        return self._adapter

    @property
    def adapter_class(self):
        """
        :return: the ``class`` of the :class:`xml4h.impls._XmlImplAdapter`
            subclass implementation that mediates operations on the node in
            the underlying XML implementation.
        """
        return self._adapter.__class__

    @property
    def document(self):
        """
        :return: the :class:`Document` node that contains this node,
            or ``self`` if this node is the document.
        """
        if self.is_document:
            return self
        return self.adapter.wrap_document(self.adapter.impl_document)

    @property
    def root(self):
        """
        :return: the root :class:`Element` node of the document that
            contains this node, or ``self`` if this node is the root element.
        """
        if self.is_root:
            return self
        return self.adapter.wrap_node(
            self.adapter.impl_root_element, self.adapter.impl_document)

    @property
    def is_root(self):
        """:return: *True* if this node is the document's root element"""
        return self.impl_node == self.adapter.impl_root_element

    @property
    def node_type(self):
        """
        :return: an int constant value that identifies the type of this node,
            such as :data:`ELEMENT_NODE` or :data:`TEXT_NODE`.
        """
        return self._node_type

    def is_type(self, node_type_constant):
        """
        :return: *True* if this node's int type matches the given value.
        """
        return self.node_type == node_type_constant

    @property
    def is_element(self):
        """
        :return: *True* if this is an :class:`Element` node.
        """
        return self.is_type(ELEMENT_NODE)

    @property
    def is_attribute(self):
        """
        :return: *True* if this is an :class:`Attribute` node.
        """
        return self.is_type(ATTRIBUTE_NODE)

    @property
    def is_text(self):
        """
        :return: *True* if this is a :class:`Text` node.
        """
        return self.is_type(TEXT_NODE)

    @property
    def is_cdata(self):
        """
        :return: *True* if this is a :class:`CDATA` node.
        """
        return self.is_type(CDATA_NODE)

    @property
    def is_entity_reference(self):
        """
        :return: *True* if this is an :class:`EntityReference` node.
        """
        return self.is_type(ENTITY_REFERENCE_NODE)

    @property
    def is_entity(self):
        """
        :return: *True* if this is an :class:`Entity` node.
        """
        return self.is_type(ENTITY_NODE)

    @property
    def is_processing_instruction(self):
        """
        :return: *True* if this is a :class:`ProcessingInstruction` node.
        """
        return self.is_type(PROCESSING_INSTRUCTION_NODE)

    @property
    def is_comment(self):
        """
        :return: *True* if this is a :class:`Comment` node.
        """
        return self.is_type(COMMENT_NODE)

    @property
    def is_document(self):
        """
        :return: *True* if this is a :class:`Document` node.
        """
        return self.is_type(DOCUMENT_NODE)

    @property
    def is_document_type(self):
        """
        :return: *True* if this is a :class:`DocumentType` node.
        """
        return self.is_type(DOCUMENT_TYPE_NODE)

    @property
    def is_document_fragment(self):
        """
        :return: *True* if this is a :class:`DocumentFragment` node.
        """
        return self.is_type(DOCUMENT_FRAGMENT_NODE)

    @property
    def is_notation(self):
        """
        :return: *True* if this is a :class:`Notation` node.
        """
        return self.is_type(NOTATION_NODE)

    def _convert_nodelist(self, nodelist):
        """
        Convert a list of underlying implementation nodes into a list of
        *xml4h* wrapper nodes.
        """
        # TODO Do something more efficient here, lazy wrapping?
        return [self.adapter.wrap_node(n, self.adapter.impl_document)
                for n in nodelist]

    @property
    def parent(self):
        """
        :return: the parent of this node, or *None* of the node has no parent.
        """
        parent_impl_node = self.adapter.get_node_parent(self.impl_node)
        return self.adapter.wrap_node(
            parent_impl_node, self.adapter.impl_document)

    @property
    def ancestors(self):
        """
        :return: the ancestors of this node in a list ordered by proximity to
            this node, that is: parent, grandparent, great-grandparent etc.
        """
        ancestors = []
        p = self.parent
        while p:
            ancestors.append(p)
            p = p.parent
        return ancestors

    def children_in_ns(self, ns_uri=None):
        """
        Return child nodes that belong to this node and that are in the
        given namespace.

        :param ns_uri: a namespace URI used to filter the child nodes.
            If *None* all child nodes are returned regardless of namespace.
        :type ns_uri: string or None
        """
        nodelist = self.adapter.get_node_children(self.impl_node)
        if ns_uri is not None:
            nodelist = filter(
                lambda x: self.adapter.get_node_namespace_uri(x) == ns_uri,
                nodelist)
        return self._convert_nodelist(nodelist)

    @property
    def children(self):
        """
        :return: a list of this node's child nodes.
        """
        return self.children_in_ns(None)

    @property
    def attributes(self):
        return None

    @property
    def attribute_nodes(self):
        return None

    def siblings_in_ns(self, ns_uri=None):
        """
        Return nodes that are siblings of this node and that are in the
        given namespace.

        :param ns_uri: a namespace URI used to filter the sibling nodes.
            If *None* all sibling nodes are returned regardless of namespace.
        :type ns_uri: string or None
        """
        nodelist = self.adapter.get_node_children(self.parent.impl_node)
        return self._convert_nodelist(
            [n for n in nodelist if n != self.impl_node])

    @property
    def siblings(self):
        """
        :return: a list of this node's sibling nodes.
        """
        return self.siblings_in_ns(None)

    @property
    def siblings_before(self):
        """
        :return: a list of this node's siblings that occur *before* this
            node in the DOM.
        """
        nodelist = self.adapter.get_node_children(self.parent.impl_node)
        before_nodelist = []
        for n in nodelist:
            if n == self.impl_node:
                break
            before_nodelist.append(n)
        return self._convert_nodelist(before_nodelist)

    @property
    def siblings_after(self):
        """
        :return: a list of this node's siblings that occur *after* this
            node in the DOM.
        """
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
        """
        :return: this node's namespace URI or *None*.
        """
        return self.adapter.get_node_namespace_uri(self.impl_node)

    ns_uri = namespace_uri  # Alias
    """Alias for :meth:`namespace_uri`"""

    @property
    def current_namespace_uri(self):
        """
        :return: the URI of the namespace this node belongs to, directly or
            through an ancestor node. *None* if node is not in a namespace.
        """
        curr_node = self
        while curr_node:
            if curr_node.namespace_uri is not None:
                return self.namespace_uri
            curr_node = curr_node.parent
        return None

    def delete(self):
        """
        Delete this node from the owning document.
        """
        self.adapter.remove_node_child(
            self.adapter.get_node_parent(self.impl_node), self.impl_node,
            destroy_node=True)

    def find(self, name=None, ns_uri=None, first_only=False):
        """
        Find :class:`Element` node descendants of this node, with optional
        constraints to limit the results.

        :param name: limit results to elements with this name.
            If *None* or ``'*'`` all element names are matched.
        :type name: string or None
        :param ns_uri: limit results to elements within this namespace URI.
            If *None* all elements are matched, regardless of namespace.
        :type ns_uri: string or None
        :param bool first_only: if *True* only return the first result node
            or *None* if there is no matching node.

        :returns: a list of :class:`Element` nodes matching any given
            constraints, or a single node if ``first_only=True``.
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
        """
        Find the first :class:`Element` node descendant of this node that
        matches any optional constraints.

        Delegates to :meth:`find` with ``first_only=True``.
        """
        return self.find(name=name, ns_uri=ns_uri, first_only=True)

    def find_doc(self, name=None, ns_uri=None, first_only=False):
        """
        Find :class:`Element` node descendants of the document containing
        this node, with optional constraints to limit the results.

        Delegates to :meth:`find` applied to this node's owning document.
        """
        return self.document.find(name=name, ns_uri=ns_uri,
            first_only=first_only)

    # Methods that operate on this Node implementation adapter

    def write(self, writer=None, encoding='utf-8', indent=0, newline='',
            omit_declaration=False, node_depth=0, quote_char='"'):
        """
        Serialize this node and its descendants to text, writing
        the output to a given *writer* or to stdout.

        :param writer: an object such as a file or stream to which XML text
            is sent. If *None* text is sent to :attr:`sys.stdout`.
        :type writer: a file, stream, etc or None
        :param string encoding: the character encoding for serialized text.
        :param indent: indentation prefix to apply to descendent nodes for
            pretty-printing. The value can take many forms:

            - *int*: the number of spaces to indent. 0 means no indent.
            - *string*: a literal prefix for indented nodes, such as ``\\t``.
            - *bool*: no indent if *False*, four spaces indent if *True*.
            - *None*: no indent
        :type indent: string, int, bool, or None
        :param newline: the string value used to separate lines of output.
            The value can take a number of forms:

            - *string*: the literal newline value, such as ``\\n`` or ``\\r``.
              An empty string means no newline.
            - *bool*: no newline if *False*, ``\\n`` newline if *True*.
            - *None*: no newline.
        :type newline: string, bool, or None
        :param boolean omit_declaration: if *True* the XML declaration header
            is omitted, otherwise it is included. Note that the declaration is
            only output when serializing an :class:`xml4h.nodes.Document` node.
        :param int node_depth: the indentation level to start at, such as 2 to
            indent output as if the given *node* has two ancestors.
            This parameter will only be useful if you need to output XML text
            fragments that can be assembled into a document.  This parameter
            has no effect unless indentation is applied.
        :param string quote_char: the character that delimits quoted content.
            You should never need to mess with this.

        Delegates to :func:`xml4h.writer.write_node` applied to this node.
        """
        xml4h.write_node(self,
            writer=writer, encoding=encoding, indent=indent,
            newline=newline, omit_declaration=omit_declaration,
            node_depth=node_depth, quote_char=quote_char)

    def write_doc(self, *args, **kwargs):
        """
        Serialize to text the document containing this node, writing
        the output to a given *writer* or stdout.

        Delegates to :meth:`write`
        """
        self.document.write(*args, **kwargs)

    def xml(self, indent=4, **kwargs):
        """
        :return: this node as XML text.

        Delegates to :meth:`write`
        """
        writer = StringIO()
        self.write(writer, indent=indent, **kwargs)
        return writer.getvalue()

    def xml_doc(self, **kwargs):
        """
        :return: the document containing this node as XML text.

        Delegates to :meth:`xml`
        """
        return self.document.xml(**kwargs)


class NodeAttrAndChildElementLookupsMixin(object):
    """
    Perform "magical" lookup of a node's attributes via dict-style keyword
    reference, and child elements via class attribute reference.
    """

    def __getitem__(self, attr_name):
        """
        Retrieve this node's attribute value by name using dict-style keyword
        lookup.

        :param string attr_name: name of the attribute.

        :raise: IndexError if the node has no such attribute.
        """
        result = self.attributes[attr_name]
        if result is None:
            raise IndexError()
        else:
            return result

    def __getattr__(self, child_name):
        """
        Retrieve this node's child element by tag name regardless of the
        elements namespace, assuming the name given doesn't match an existing
        attribute of this class.

        :param string child_name: tag name of the child element. The name must
            match the following pattern rules for *xml4h* to attempt a child
            element lookup, otherwise an AttributeError will be raised
            immediately:
            - name contains one or more uppercase characters, or
            - name is all lowercase but ends with a single underscore character
            - **in all cases** the name does not begin with an underscore
              character.
        :return: the type of the return value depends on how many child
            elements match the name:
            - a single :class:`Element` node if only one child element matches
            - a list of :class:`Element` nodes if there is more than 1 match.

        :raise: AttributeError if the node has no child element with the given
            name, or if the given name does not match the required pattern.
        """
        if child_name.startswith('_'):
            # Never match names with underscore leaders, for safety
            pass
        elif child_name != child_name.lower() or child_name.endswith('_'):
            # Names with uppercase characters or trailing '_' are fair game
            results = self.get(child_name)
            if len(results) == 1:
                return results[0]
            elif len(results) > 1:
                return results
        raise AttributeError(
            "'%s' object has no attribute '%s'"
            % (self.__class__.__name__, child_name))

    def get(self, child_name, first_only=False):
        """
        Retrieve this node's child element by tag name regardless of the
        elements namespace.

        :param string child_name: tag name of the child element.
        :param book first_only: if True, return only the first matching
            child node instead of a list of nodes.
        :return: the type of the return value depends on the value of the
            ``first_only`` parameter and how many child elements match:

            - if ``first_only=False`` return a list of :class:`Element` nodes;
              this list will be empty if there are no matching child elements.
            - if ``first_only=True`` and at least one child element matches,
              return the first matching :class:`Element` node
            - if ``first_only=True`` and there are no matching child elements,
              return *None*

        :raise: AttributeError if the node has no child element with the given
            name, or if the given name does not match the required pattern.
        """
        results = [c for c in self.children
                   if isinstance(c, Element) and c.local_name == child_name]
        if first_only:
            return results[0] if results else None
        else:
            return results

    def get_first(self, child_name):
        """
        :return: this node's first child element matching the given tag name
            regardless of the elements namespace, or *None* if there are no
            matching nodes.

        Delegates to :meth:`get`.
        """
        return self.get(child_name, first_only=True)


class XPathMixin(object):

    def _maybe_wrap_node(self, node):
        # Don't try and wrap base types (e.g. attribute values or node text)
        if isinstance(node, (basestring, int, long, float)):
            return node
        else:
            return self.adapter.wrap_node(node, self.adapter.impl_document)

    def xpath(self, xpath, **kwargs):
        result = self.adapter.xpath_on_node(self.impl_node, xpath, **kwargs)
        if isinstance(result, (list, tuple)):
            return [self._maybe_wrap_node(r) for r in result]
        else:
            return self._maybe_wrap_node(result)


class Document(Node, NodeAttrAndChildElementLookupsMixin, XPathMixin):
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


class NameValueNodeMixin(Node):

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


class Text(NameValueNodeMixin):
    _node_type = TEXT_NODE


class CDATA(NameValueNodeMixin):
    _node_type = CDATA_NODE


class Entity(NameValueNodeMixin):
    _node_type = ENTITY_NODE


class Comment(NameValueNodeMixin):
    _node_type = COMMENT_NODE


class Attribute(NameValueNodeMixin):
    _node_type = ATTRIBUTE_NODE

    # Cannot set/change name of attribute
    @property
    def name(self):
        return super(Attribute, self).name

    # Cannot set/change value of attribute
    @property
    def value(self):
        return super(Attribute, self).value


class ProcessingInstruction(NameValueNodeMixin):
    _node_type = PROCESSING_INSTRUCTION_NODE

    target = NameValueNodeMixin.name

    data = NameValueNodeMixin.value


class Element(NameValueNodeMixin,
        NodeAttrAndChildElementLookupsMixin, XPathMixin):
    """
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.
    """
    _node_type = ELEMENT_NODE

    @property
    def builder(self):
        return xml4h.Builder(self)

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
        """
        Add one or more attributes to the current element node.
        """
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

    attrib = attributes  # Alias

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
        """
        Add a child element to the current element node and return the child.
        """
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
        """
        Add a text node to the current element node.

        :param text: string data content for the node
        :param type: basestring, or any object that can be converted to
                     a string by :func:`unicode`
        """
        if not isinstance(text, basestring):
            text = unicode(text)
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

    def __unicode__(self):
        return u'<%s.%s: %s>' % (
            self.__class__.__module__, self.__class__.__name__,
            self.to_dict)

    def __str__(self):
        # TODO Degrade non-ASCII characters gracefully
        return str(self.__unicode__())

    def __repr__(self):
        return self.__str__()

    def keys(self):
        return [self.adapter.get_node_name(a) for a in self.impl_attributes]

    def values(self):
        return [self.adapter.get_node_value(a) for a in self.impl_attributes]

    def items(self):
        sorted_keys = sorted(self.keys())
        return [(k, self[k]) for k in sorted_keys]

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
    def to_dict(self):
        """Return attribute dictionary as an ordered dict"""
        return collections.OrderedDict(self.items())

    @property
    def element(self):
        return self.adapter.wrap_node(
            self.impl_element, self.adapter.impl_document)

    @property
    def impl_attributes(self):
        return self.adapter.get_node_attributes(self.impl_element)
