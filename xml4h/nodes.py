import six
import collections
import functools

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
        :param adapter: the :class:`xml4h.impls.XmlImplAdapter`
            subclass implementation to mediate operations on the node in
            the underlying XML implementation.
        """
        if node is None:
            raise xml4h.exceptions.IncorrectArgumentTypeException(
                node, [object])
        if adapter is None:
            raise xml4h.exceptions.IncorrectArgumentTypeException(
                adapter, [object])
        self._impl_node = node
        self._adapter = adapter

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, Node):
            return False
        return (self.impl_document == other.impl_document
            and self.impl_node == other.impl_node)

    def __repr__(self):
        return '<%s.%s>' % (
            self.__class__.__module__, self.__class__.__name__)

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
        :return: the :class:`xml4h.impls.XmlImplAdapter` subclass
            implementation that mediates operations on the node in the
            underlying XML implementation.
        """
        return self._adapter

    @property
    def adapter_class(self):
        """
        :return: the ``class`` of the :class:`xml4h.impls.XmlImplAdapter`
            subclass implementation that mediates operations on the node in
            the underlying XML implementation.
        """
        return self._adapter.__class__

    def has_feature(self, feature_name):
        """
        :return: *True* if a named feature is supported by the adapter\
                 implementation underlying this node.
        """
        return self.adapter.has_feature(feature_name)

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
            self.adapter.impl_root_element, self.adapter.impl_document,
            self.adapter)

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

    def _convert_nodelist(self, impl_nodelist):
        """
        Convert a list of underlying implementation nodes into a list of
        *xml4h* wrapper nodes.
        """
        nodelist = [
            self.adapter.wrap_node(n, self.adapter.impl_document, self.adapter)
            for n in impl_nodelist]
        return NodeList(nodelist)

    @property
    def parent(self):
        """
        :return: the parent of this node, or *None* of the node has no parent.
        """
        parent_impl_node = self.adapter.get_node_parent(self.impl_node)
        return self.adapter.wrap_node(
            parent_impl_node, self.adapter.impl_document, self.adapter)

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
        return NodeList(ancestors)

    @property
    def children(self):
        """
        :return: a :class:`NodeList` of this node's child nodes.
        """
        impl_nodelist = self.adapter.get_node_children(self.impl_node)
        return self._convert_nodelist(impl_nodelist)

    def child(self, local_name=None, name=None, ns_uri=None, node_type=None,
            filter_fn=None):
        """
        :return: the first child node matching the given constraints, or \
                 *None* if there are no matching child nodes.

        Delegates to :meth:`NodeList.filter`.
        """
        return self.children(name=name, local_name=local_name, ns_uri=ns_uri,
            node_type=node_type, filter_fn=filter_fn, first_only=True)

    @property
    def attributes(self):
        return None

    @property
    def attribute_nodes(self):
        return None

    @property
    def siblings(self):
        """
        :return: a list of this node's sibling nodes.
        :rtype: NodeList
        """
        impl_nodelist = self.adapter.get_node_children(self.parent.impl_node)
        return self._convert_nodelist(
            [n for n in impl_nodelist if n != self.impl_node])

    @property
    def siblings_before(self):
        """
        :return: a list of this node's siblings that occur *before* this
            node in the DOM.
        """
        impl_nodelist = self.adapter.get_node_children(self.parent.impl_node)
        before_nodelist = []
        for n in impl_nodelist:
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
        impl_nodelist = self.adapter.get_node_children(self.parent.impl_node)
        after_nodelist = []
        is_after_myself = False
        for n in impl_nodelist:
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

    def delete(self, destroy=True):
        """
        Delete this node from the owning document.

        :param bool destroy: if True the child node will be destroyed in
            addition to being removed from the document.

        :returns: the removed child node, or *None* if the child was destroyed.
        """
        removed_child = self.adapter.remove_node_child(
            self.adapter.get_node_parent(self.impl_node), self.impl_node,
            destroy_node=destroy)
        if removed_child is not None:
            return self.adapter.wrap_node(removed_child, None, self.adapter)
        else:
            return None

    def clone_node(self, node):
        """
        Clone a node from another document to become a child of this node, by
        copying the node's data into this document but leaving the node
        untouched in the source document. The node to be cloned can be
        a :class:`Node` based on the same underlying XML library implementation
        and adapter, or a "raw" node from that implementation.

        :param node: the node in another document to clone.
        :type node: xml4h or implementation node
        """
        if isinstance(node, xml4h.nodes.Node):
            child_impl_node = node.impl_node
        else:
            child_impl_node = node  # Assume it's a valid impl node
        self.adapter.import_node(self.impl_node, child_impl_node, clone=True)

    def transplant_node(self, node):
        """
        Transplant a node from another document to become a child of this node,
        removing it from the source document.  The node to be transplanted can
        be a :class:`Node` based on the same underlying XML library
        implementation and adapter, or a "raw" node from that implementation.

        :param node: the node in another document to transplant.
        :type node: xml4h or implementation node
        """
        if isinstance(node, xml4h.nodes.Node):
            child_impl_node = node.impl_node
            original_parent_impl_node = node.parent.impl_node
        else:
            child_impl_node = node  # Assume it's a valid impl node
            original_parent_impl_node = self.adapter.get_node_parent(node)
        self.adapter.import_node(self.impl_node, child_impl_node,
            original_parent_impl_node, clone=False)

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
        impl_nodelist = self.adapter.find_node_elements(
            self.impl_node, name=name, ns_uri=ns_uri)
        if first_only:
            if impl_nodelist:
                return self.adapter.wrap_node(
                    impl_nodelist[0], self.adapter.impl_document, self.adapter)
            else:
                return None
        return self._convert_nodelist(impl_nodelist)

    def find_first(self, name=None, ns_uri=None):
        """
        Find the first :class:`Element` node descendant of this node that
        matches any optional constraints, or None if there are no matching
        elements.

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

    def write(self, writer, encoding='utf-8', indent=0, newline='',
            omit_declaration=False, node_depth=0, quote_char='"'):
        """
        Serialize this node and its descendants to text, writing
        the output to the given *writer*.

        :param writer: a file or stream to which XML text is written.
        :type writer: a file, stream, etc
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
            writer, encoding=encoding, indent=indent,
            newline=newline, omit_declaration=omit_declaration,
            node_depth=node_depth, quote_char=quote_char)

    def write_doc(self, writer, *args, **kwargs):
        """
        Serialize to text the document containing this node, writing
        the output to the given *writer*.

        :param writer: a file or stream to which XML text is written.
        :type writer: a file, stream, etc

        Delegates to :meth:`write`
        """
        self.document.write(writer, *args, **kwargs)

    def xml(self, encoding='utf-8', indent=4, **kwargs):
        """
        :return: this node as an XML string.

        Delegates to :meth:`write`
        """
        # Use string writer if `encoding` is unset, unusual but possible...
        if encoding is None:
            writer = six.StringIO()
        # ...otherwise and by default, use a bytes writer
        else:
            writer = six.BytesIO()
        self.write(writer, encoding=encoding, indent=indent, **kwargs)
        xml_bytes = writer.getvalue()
        if encoding:
            return xml_bytes.decode(encoding)
        else:
            return xml_bytes

    def xml_doc(self, encoding='utf-8', **kwargs):
        """
        :return: the document containing this node as an XML string.

        Delegates to :meth:`xml`
        """
        return self.document.xml(encoding=encoding, **kwargs)


class NodeAttrAndChildElementLookupsMixin(object):
    """
    Perform "magical" lookup of a node's attributes via dict-style keyword
    reference, and child elements via class attribute reference.
    """

    def __getitem__(self, attr_name):
        """
        Retrieve this node's attribute value by name using dict-style keyword
        lookup.

        :param string attr_name: name of the attribute. If the attribute has
            a namespace prefix that must be included, in other words the name
            must be a qname not local name.

        :raise: KeyError if the node has no such attribute.
        """
        result = self.attributes[attr_name]
        if result is None:
            raise KeyError(attr_name)
        else:
            return result

    def __getattr__(self, child_name):
        """
        Retrieve this node's child element by tag name regardless of the
        elements namespace, assuming the name given doesn't match an existing
        attribute or method.

        :param string child_name: tag name of the child element to look up.
            To avoid name clashes with class attributes the child name may
            includes a trailing underscore (``_``) character, which is removed
            to get the real child tag name.
            The child name must not begin with underscore characters.

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
        else:
            # If name is munged with trailing underscore, remove it
            if child_name.endswith('_'):
                child_name = child_name[:-1]
            results = self.children(local_name=child_name, node_type=Element)
            if len(results) == 1:
                return results[0]
            elif len(results) > 1:
                return results
        raise AttributeError(
            "%s object has no attribute '%s'" % (self, child_name))


class XPathMixin(object):
    """
    Provide :meth:`xpath` method to nodes that support XPath searching.
    """

    def _maybe_wrap_node(self, node):
        # Don't try and wrap base types (e.g. attribute values or node text)
        if isinstance(node, (str, int, float)):
            return node
        else:
            return self.adapter.wrap_node(
                node, self.adapter.impl_document, self.adapter)

    def xpath(self, xpath, **kwargs):
        """
        Perform an XPath query on the current node.

        :param string xpath: XPath query.
        :param dict kwargs: Optional keyword arguments that are passed through
            to the underlying XML library implementation.

        :return: results of the query as a list of :class:`Node` objects, or
            a list of base type objects if the XPath query does not reference
            node objects.
        """
        result = self.adapter.xpath_on_node(self.impl_node, xpath, **kwargs)
        if isinstance(result, (list, tuple)):
            return [self._maybe_wrap_node(r) for r in result]
        else:
            return self._maybe_wrap_node(result)


class Document(Node, NodeAttrAndChildElementLookupsMixin, XPathMixin):
    """
    Node representing an entire XML document.
    """
    _node_type = DOCUMENT_NODE
    # TODO: doc_type, document_element


class DocumentType(Node):
    """
    Node representing the type of an XML document.
    """
    _node_type = DOCUMENT_TYPE_NODE
    # TODO: name, entities, notations, public_id, system_id


class DocumentFragment(Node):
    """
    Node representing an XML document fragment.
    """
    _node_type = DOCUMENT_FRAGMENT_NODE
    # TODO


class Notation(Node):
    """
    Node representing a notation in an XML document.
    """
    _node_type = NOTATION_NODE
    # TODO: public_id, system_id


class Entity(Node):
    """
    Node representing an entity in an XML document.
    """
    _node_type = ENTITY_NODE
    # TODO: public_id, system_id

    @property
    def notation_name(self):
        return self.name


class EntityReference(Node):
    """
    Node representing an entity reference in an XML document.
    """
    _node_type = ENTITY_REFERENCE_NODE
    # TODO


class NameValueNodeMixin(Node):
    """
    Provide methods to access node name and value attributes, where the node
    name may also be composed of "prefix" and "local" components.
    """

    def __repr__(self):
        return '<%s.%s: "%s">' % (
            self.__class__.__module__, self.__class__.__name__,
            self.name)

    def _tounicode(self, value):
        if value is None or isinstance(value, six.string_types):
            return value
        else:
            return six.text_type(value)

    @property
    def prefix(self):
        """
        :return: the namespace prefix component of a node name, or None.
        """
        return self._tounicode(
            self.adapter.get_node_name_prefix(self.impl_node))

    @property
    def local_name(self):
        """
        :return: the local component of a node name excluding any prefix.
        """
        return self._tounicode(
            self.adapter.get_node_local_name(self.impl_node))

    @property
    def name(self):
        """
        Get the name of a node, possibly including prefix and local components.
        """
        return self._tounicode(
            self.adapter.get_node_name(self.impl_node))

    @property
    def value(self):
        """
        Get or set the value of a node.
        """
        return self._tounicode(
            self.adapter.get_node_value(self.impl_node))

    @value.setter
    def value(self, value):
        self.adapter.set_node_value(self.impl_node, value)


class Text(NameValueNodeMixin):
    """
    Node representing text content in an XML document.
    """
    _node_type = TEXT_NODE


class CDATA(NameValueNodeMixin):
    """
    Node representing character data in an XML document.
    """
    _node_type = CDATA_NODE


class Comment(NameValueNodeMixin):
    """
    Node representing a comment in an XML document.
    """
    _node_type = COMMENT_NODE


class Attribute(NameValueNodeMixin):
    """
    Node representing an attribute of a :class:`Document` or
    :class:`Element` node.
    """
    _node_type = ATTRIBUTE_NODE


class ProcessingInstruction(NameValueNodeMixin):
    """
    Node representing a processing instruction in an XML document.
    """
    _node_type = PROCESSING_INSTRUCTION_NODE

    target = NameValueNodeMixin.name

    data = NameValueNodeMixin.value


class Element(NameValueNodeMixin,
        NodeAttrAndChildElementLookupsMixin, XPathMixin):
    """
    Node representing an element in an XML document, with support for
    manipulating and adding content to the element.
    """
    _node_type = ELEMENT_NODE

    @property
    def builder(self):
        """
        :return: a :class:`~xml4h.builder.Builder` representing this element
            with convenience methods for adding XML content.
        """
        return xml4h.Builder(self)

    @property
    def text(self):
        """
        Get or set the text content of this element.
        """
        return self.adapter.get_node_text(self.impl_node)

    @text.setter
    def text(self, text):
        self.adapter.set_node_text(self.impl_node, text)

    def _set_element_attributes(self, element,
            attr_obj=None, ns_uri=None, **attr_dict):
        if attr_obj is not None:
            if isinstance(attr_obj, dict):
                attr_dict.update(attr_obj)
            elif isinstance(attr_obj, (list, tuple)):
                for n, v in attr_obj:
                    attr_dict[n] = v
            else:
                raise xml4h.exceptions.IncorrectArgumentTypeException(
                    attr_obj, [dict, list, tuple])

        # Always process 'xmlns' namespace definitions first, in case other
        # attributes belong to a newly-defined namespace
        # TODO Modern equivalent for this legacy `cmp` method re-implementation
        def cmp(a, b):
            # https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons
            return (a > b) - (a < b)

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

        # https://docs.python.org/3/library/functools.html#functools.cmp_to_key
        # TODO Modern equivalent for this custom sorting `cmp` function
        _xmlns_first = functools.cmp_to_key(_xmlns_first)
        
        attr_list = sorted(list(attr_dict.items()), key=_xmlns_first)

        # Add attributes
        for attr_name, v in attr_list:
            prefix, name, my_ns_uri = self.adapter.get_ns_info_from_node_name(
                attr_name, element)
            if ' ' in name:
                raise ValueError("Invalid attribute name value contains space")
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
            if not isinstance(v, six.string_types):
                v = six.text_type(v)
            if prefix:
                qname = '%s:%s' % (prefix, name)
            else:
                qname = name
            self.adapter.set_node_attribute_value(
                element, qname, v, ns_uri=my_ns_uri)

    def set_attributes(self, attr_obj=None, ns_uri=None, **attr_dict):
        """
        Add or update this element's attributes, where attributes can be
        specified in a number of ways.

        :param attr_obj: a dictionary or list of attribute name/value pairs.
        :type attr_obj: dict, list, tuple, or None
        :param ns_uri: a URI defining a namespace for the new attributes.
        :type ns_uri: string or None
        :param dict attr_dict: attribute name and values specified as keyword
            arguments.
        """
        self._set_element_attributes(self.impl_node,
            attr_obj=attr_obj, ns_uri=ns_uri, **attr_dict)

    @property
    def attributes(self):
        """
        Get or set this element's attributes as name/value pairs.

        .. note::
            Setting element attributes via this accessor will **remove**
            any existing attributes, as opposed to the :meth:`set_attributes`
            method which only updates and replaces them.
        """
        attr_impl_nodes = self.adapter.get_node_attributes(self.impl_node)
        return AttributeDict(attr_impl_nodes, self.impl_node, self.adapter)

    @attributes.setter
    def attributes(self, attr_obj):
        # Remove existing attributes, leaving namespace definitions until last
        # to avoid clobbering the namespace of other attributes
        for attr_name in [a for a in self.attributes if 'xmlns' not in a]:
            self.adapter.remove_node_attribute(self.impl_node, attr_name)
        for attr_name in self.attributes:
            self.adapter.remove_node_attribute(self.impl_node, attr_name)
        # Add new attributes
        self._set_element_attributes(self.impl_node, attr_obj=attr_obj)

    attrib = attributes  # Alias
    """
    Alias of :meth:`attributes`
    """

    attrs = attributes  # Alias
    """
    Alias of :meth:`attributes`
    """

    @property
    def attribute_nodes(self):
        """
        :return: a list of this element's attributes as
            :class:`Attribute` nodes.
        """
        impl_attr_nodes = self.adapter.get_node_attributes(self.impl_node)
        wrapped_attr_nodes = [
            self.adapter.wrap_node(a, self.adapter.impl_document, self.adapter)
            for a in impl_attr_nodes]
        return sorted(wrapped_attr_nodes, key=lambda x: x.name)

    def attribute_node(self, name, ns_uri=None):
        """
        :param string name: the name of the attribute to return.
        :param ns_uri: a URI defining a namespace constraint on the attribute.
        :type ns_uri: string or None

        :return: this element's attributes that match ``ns_uri`` as
            :class:`Attribute` nodes.
        """
        attr_impl_node = self.adapter.get_node_attribute_node(
            self.impl_node, name, ns_uri)
        return self.adapter.wrap_node(
            attr_impl_node, self.adapter.impl_document, self.adapter)

    def _add_ns_prefix_attr(self, element, prefix, ns_uri):
        if prefix is None:
            ns_name = 'xmlns'
            self.adapter.set_node_namespace_uri(element, ns_uri)
        else:
            ns_name = 'xmlns:%s' % prefix
        self._set_element_attributes(element,
            {ns_name: ns_uri}, ns_uri=self.XMLNS_URI)

    def set_ns_prefix(self, prefix, ns_uri):
        """
        Define a namespace prefix that will serve as shorthand for the given
        namespace URI in element names.

        :param string prefix: prefix that will serve as an alias for a
            the namespace URI.
        :param string ns_uri: namespace URI that will be denoted by the
            prefix.
        """
        self._add_ns_prefix_attr(self.impl_node, prefix, ns_uri)

    def add_element(self, name, ns_uri=None, attributes=None,
            text=None, before_this_element=False):
        """
        Add a new child element to this element, with an optional namespace
        definition. If no namespace is provided the child will be assigned
        to the default namespace.

        :param string name: a name for the child node. The name may be used
            to apply a namespace to the child by including:

            - a prefix component in the name of the form
              ``ns_prefix:element_name``, where the prefix has already been
              defined for a namespace URI (such as via :meth:`set_ns_prefix`).
            - a literal namespace URI value delimited by curly braces, of
              the form ``{ns_uri}element_name``.
        :param ns_uri: a URI specifying the new element's namespace. If the
            ``name`` parameter specifies a namespace this parameter is ignored.
        :type ns_uri: string or None
        :param attributes: collection of attributes to assign to the new child.
        :type attributes: dict, list, tuple, or None
        :param text: text value to assign to the new child.
        :type text: string or None
        :param bool before_this_element: if *True* the new element is
            added as a sibling preceding this element, instead of as a child.
            In other words, the new element will be a child of this element's
            parent node, and will immediately precent this element in the DOM.

        :return: the new child as a an :class:`Element` node.
        """
        # Determine local name, namespace and prefix info from tag name
        prefix, local_name, node_ns_uri = \
            self.adapter.get_ns_info_from_node_name(name, self.impl_node)
        if prefix:
            qname = '%s:%s' % (prefix, local_name)
        else:
            qname = local_name
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
        if not prefix and '}' in name:
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
        return self.adapter.wrap_node(
            child_elem, self.adapter.impl_document, self.adapter)

    def _add_text(self, element, text):
        text_node = self.adapter.new_impl_text(text)
        self.adapter.add_node_child(element, text_node)

    def add_text(self, text):
        """
        Add a text node to this element.

        Adding text with this method is subtly different from assigning a new
        text value with :meth:`text` accessor, because it "appends" to rather
        than replacing this element's set of text nodes.

        :param text: text content to add to this element.
        :param type: string or anything that can be coerced by :func:`unicode`.
        """
        if not isinstance(text, six.string_types):
            text = six.text_type(text)
        self._add_text(self.impl_node, text)

    def _add_comment(self, element, text):
        comment_node = self.adapter.new_impl_comment(text)
        self.adapter.add_node_child(element, comment_node)

    def add_comment(self, text):
        """
        Add a comment node to this element.

        :param string text: text content to add as a comment.
        """
        self._add_comment(self.impl_node, text)

    def _add_instruction(self, element, target, data):
        instruction_node = self.adapter.new_impl_instruction(target, data)
        self.adapter.add_node_child(element, instruction_node)

    def add_instruction(self, target, data):
        """
        Add an instruction node to this element.

        :param string text: text content to add as an instruction.
        """
        self._add_instruction(self.impl_node, target, data)

    def _add_cdata(self, element, data):
        cdata_node = self.adapter.new_impl_cdata(data)
        self.adapter.add_node_child(element, cdata_node)

    def add_cdata(self, data):
        """
        Add a character data node to this element.

        :param string data: text content to add as character data.
        """
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
        if not isinstance(value, str):
            value = str(value)
        self.adapter.set_node_attribute_value(
            self.impl_element, name, value, ns_uri)

    def __delitem__(self, name):
        prefix, name, ns_uri = self.adapter.get_ns_info_from_node_name(
            name, self.impl_element)
        self.adapter.remove_node_attribute(self.impl_element, name, ns_uri)

    def __iter__(self):
        for k in list(self.keys()):
            yield k

    iterkeys = __iter__  # Alias, per Python docs recommendation

    def __contains__(self, name):
        prefix, name, ns_uri = self.adapter.get_ns_info_from_node_name(
            name, self.impl_element)
        return self.adapter.has_node_attribute(self.impl_element, name, ns_uri)

    def __repr__(self):
        return '<%s.%s: %s>' % (
            self.__class__.__module__, self.__class__.__name__,
            list(self.to_dict.items()))

    def keys(self):
        """
        :return: a list of attribute name strings.
        """
        return [self.adapter.get_node_name(a) for a in self.impl_attributes]

    def values(self):
        """
        :return: a list of attribute value strings.
        """
        return [self.adapter.get_node_value(a) for a in self.impl_attributes]

    def items(self):
        """
        :return: a list of name/value attribute pairs sorted by attribute name.
        """
        sorted_keys = sorted(self.keys())
        return [(k, self[k]) for k in sorted_keys]

    def namespace_uri(self, name):
        """
        :param string name: the name of an attribute to look up.

        :return: the namespace URI associated with the named attribute,
            or None.
        """
        a_node = self.adapter.get_node_attribute_node(self.impl_element, name)
        if a_node is None:
            return None
        return self.adapter.get_node_namespace_uri(a_node)

    def prefix(self, name):
        """
        :param string name: the name of an attribute to look up.

        :return: the prefix component of the named attribute's name,
            or None.
        """
        a_node = self.adapter.get_node_attribute_node(self.impl_element, name)
        if a_node is None:
            return None
        return a_node.prefix

    @property
    def to_dict(self):
        """
        :return: an :class:`~collections.OrderedDict` of attribute name/value
            pairs.
        """
        return collections.OrderedDict(list(self.items()))

    @property
    def element(self):
        """
        :return: the :class:`Element` that contains these attributes.
        """
        return self.adapter.wrap_node(
            self.impl_element, self.adapter.impl_document, self.adapter)

    @property
    def impl_attributes(self):
        """
        :return: the attribute node objects from the underlying XML
            implementation.
        """
        return self.adapter.get_node_attributes(self.impl_element)


class NodeList(list):
    """
    Custom implementation for :class:`Node` lists that provides additional
    functionality, such as node filtering.
    """

    def filter(self, local_name=None, name=None, ns_uri=None, node_type=None,
            filter_fn=None, first_only=False):
        """
        Apply filters to the set of nodes in this list.

        :param local_name: a local name used to filter the nodes.
        :type local_name: string or None
        :param name: a name used to filter the nodes.
        :type name: string or None
        :param ns_uri: a namespace URI used to filter the nodes.
            If *None* all nodes are returned regardless of namespace.
        :type ns_uri: string or None
        :param node_type: a node type definition used to filter the nodes.
        :type node_type: int node type constant, class, or None
        :param filter_fn: an arbitrary function to filter nodes in this list.
            This function must accept a single :class:`Node` argument and
            return a bool indicating whether to include the node in the
            filtered results.

            .. note:: if ``filter_fn`` is provided all other filter arguments
                are ignore.
        :type filter_fn: function or None

        :return: the type of the return value depends on the value of the
            ``first_only`` parameter and how many nodes match the filter:

            - if ``first_only=False`` return a :class:`NodeList` of filtered
              nodes, which will be empty if there are no matching nodes.
            - if ``first_only=True`` and at least one node matches,
              return the first matching :class:`Node`
            - if ``first_only=True`` and there are no matching nodes,
              return *None*
        """
        # Build our own filter function unless a custom function is provided
        if filter_fn is None:
            def filter_fn(n):
                # Test node type first in case other tests require this type
                if node_type is not None:
                    # Node type can be specified as an integer constant (e.g.
                    # ELEMENT_NODE) or a class.
                    if isinstance(node_type, int):
                        if not n.is_type(node_type):
                            return False
                    elif n.__class__ != node_type:
                        return False
                if name is not None and n.name != name:
                    return False
                if local_name is not None and n.local_name != local_name:
                    return False
                if ns_uri is not None and n.ns_uri != ns_uri:
                    return False
                return True
        # Filter nodes
        nodelist = list(filter(filter_fn, self))
        # If requested, return just the first node (or None if no nodes)
        if first_only:
            return nodelist[0] if nodelist else None
        else:
            return NodeList(nodelist)

    __call__ = filter  # Alias
    """Alias for :meth:`filter`."""

    @property
    def first(self):
        """
        :return: the first of the available children nodes, or *None* if \
                 there are no children.
        """
        if len(self) > 0:
            return self[0]
        else:
            return None
