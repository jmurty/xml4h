"""
Builder is a utility class that makes it easy to create valid, well-formed
XML documents using relatively sparse python code.  The builder class works
by wrapping an :class:`xml4h.nodes.Element` node to provide "chainable"
methods focussed specifically on adding XML content.

Each method that adds content returns a Builder instance representing the
current or the newly-added element. Behind the scenes, the builder uses the
:mod:`xml4h.nodes` node traversal and manipulation methods to add content
directly to the underlying DOM.

You will not generally create Builder instances directly, but will instead
call the :meth:`xml4h.builder` method with the name for a new root element
or with an existing :class:`xml4h.nodes.Element` node.
"""
import xml4h


class Builder(object):
    """
    Builder class that wraps an :class:`xml4h.nodes.Element` node with methods
    for adding XML content to an underlying DOM.
    """

    def __init__(self, element):
        """
        Create a Builder representing an xml4h Element node.

        :param element: Element node to represent
        :type element: :class:`xml4h.nodes.Element`
        """
        if not isinstance(element, xml4h.nodes.Element):
            raise ValueError(
                "Builder can only be created with an %s.%s instance, not %s"
                % (xml4h.nodes.Element.__module__,
                   xml4h.nodes.Element.__name__,
                   element))
        self._element = element

    @property
    def dom_element(self):
        """
        :return: the :class:`xml4h.nodes.Element` node represented by this
                 Builder.
        """
        return self._element

    @property
    def document(self):
        """
        :return: the :class:`xml4h.nodes.Document` node that contains the
                 element represented by this Builder.
        """
        return self._element.document

    @property
    def root(self):
        """
        :return: the :class:`xml4h.nodes.Element` root node ancestor of the
                 element represented by this Builder
        """
        return self._element.root

    def find(self, **kwargs):
        """
        Find descendants of the element represented by this builder that
        match the given constraints.

        :return: a list of :class:`xml4h.nodes.Element` nodes

        Delegates to :meth:`xml4h.nodes.Node.find`
        """
        return self._element.find(**kwargs)

    def find_doc(self, **kwargs):
        """
        Find nodes in this element's owning :class:`xml4h.nodes.Document`
        that match the given constraints.

        :return: a list of :class:`xml4h.nodes.Element` nodes

        Delegates to :meth:`xml4h.nodes.Node.find_doc`.
        """
        return self._element.find_doc(**kwargs)

    def write(self, *args, **kwargs):
        """
        Write XML bytes for the element represented by this builder.

        Delegates to :meth:`xml4h.nodes.Node.write`.
        """
        self.dom_element.write(*args, **kwargs)

    def write_doc(self, *args, **kwargs):
        """
        Write XML bytes for the Document containing the element
        represented by this builder.

        Delegates to :meth:`xml4h.nodes.Node.write_doc`.
        """
        self.dom_element.write_doc(*args, **kwargs)

    def xml(self, **kwargs):
        """
        :return: XML string for the element represented by this builder.

        Delegates to :meth:`xml4h.nodes.Node.xml`.
        """
        return self.dom_element.xml(**kwargs)

    def xml_doc(self, **kwargs):
        """
        :return: XML string for the Document containing the element represented
                 by this builder.

        Delegates to :meth:`xml4h.nodes.Node.xml_doc`.
        """
        return self.dom_element.xml_doc(**kwargs)

    def up(self, count_or_element_name=1):
        """
        :return: a builder representing an ancestor of the current element,
                 by default the parent element.

        :param count_or_element_name:
            when an integer, return the n'th ancestor element up to the
            document's root element.
            when a string, return the nearest ancestor element with that name,
            or the document's root element if there are no matching ancestors.
            Defaults to integer value 1 which means the immediate parent.
        :type count_or_element_name: integer or string
        """
        elem = self._element
        to_count = to_name = None
        if isinstance(count_or_element_name, int):
            to_count = count_or_element_name
        else:
            to_name = count_or_element_name
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if elem.is_root or elem.parent is None:
                break
            # Go up to element's parent
            elem = elem.parent
            # If we have a name to match and it matches, stop
            if to_name:
                if elem.name == to_name:
                    break
                continue
            # If we have a count to reach and have reached it, stop
            up_count += 1
            if up_count >= to_count:
                break
        return Builder(elem)

    def transplant(self, node):
        """
        Transplant a node from another document to become a child of
        the :class:`xml4h.nodes.Element` node represented by this Builder.

        :return: a new Builder that represents the current element \
                 (not the transplanted node).

        Delegates to :meth:`xml4h.nodes.Node.transplant_node`.
        """
        self._element.transplant_node(node)
        return self

    def clone(self, node):
        """
        Clone a node from another document to become a child of
        the :class:`xml4h.nodes.Element` node represented by this Builder.

        :return: a new Builder that represents the current element \
                 (not the cloned node).

        Delegates to :meth:`xml4h.nodes.Node.clone_node`.
        """
        self._element.clone_node(node)
        return self

    def element(self, *args, **kwargs):
        """
        Add a child element to the :class:`xml4h.nodes.Element` node
        represented by this Builder.

        :return: a new Builder that represents the child element.

        Delegates to :meth:`xml4h.nodes.Element.add_element`.
        """
        child_element = self._element.add_element(*args, **kwargs)
        return Builder(child_element)

    elem = element  # Alias
    """Alias of :meth:`element`"""

    e = element  # Alias
    """Alias of :meth:`element`"""

    def attributes(self, *args, **kwargs):
        """
        Add one or more attributes to the :class:`xml4h.nodes.Element` node
        represented by this Builder.

        :return: the current Builder.

        Delegates to :meth:`xml4h.nodes.Element.set_attributes`.
        """
        self._element.set_attributes(*args, **kwargs)
        return self

    attrs = attributes  # Alias
    """Alias of :meth:`attributes`"""

    a = attributes  # Alias
    """Alias of :meth:`attributes`"""

    def text(self, text):
        """
        Add a text node to the :class:`xml4h.nodes.Element` node
        represented by this Builder.

        :return: the current Builder.

        Delegates to :meth:`xml4h.nodes.Element.add_text`.
        """
        self._element.add_text(text)
        return self

    t = text  # Alias
    """Alias of :meth:`text`"""

    def comment(self, text):
        """
        Add a coment node to the :class:`xml4h.nodes.Element` node
        represented by this Builder.

        :return: the current Builder.

        Delegates to :meth:`xml4h.nodes.Element.add_comment`.
        """
        self._element.add_comment(text)
        return self

    c = comment  # Alias
    """Alias of :meth:`comment`"""

    def processing_instruction(self, target, data):
        """
        Add a processing instruction node to the :class:`xml4h.nodes.Element`
        node represented by this Builder.

        :return: the current Builder.

        Delegates to :meth:`xml4h.nodes.Element.add_instruction`.
        """
        self._element.add_instruction(target, data)
        return self

    instruction = processing_instruction  # Alias
    """Alias of :meth:`processing_instruction`"""

    i = instruction  # Alias
    """Alias of :meth:`processing_instruction`"""

    def cdata(self, text):
        """
        Add a CDATA node to the :class:`xml4h.nodes.Element` node
        represented by this Builder.

        :return: the current Builder.

        Delegates to :meth:`xml4h.nodes.Element.add_cdata`.
        """
        self._element.add_cdata(text)
        return self

    data = cdata  # Alias
    """Alias of :meth:`cdata`"""

    d = cdata  # Alias
    """Alias of :meth:`cdata`"""

    def ns_prefix(self, prefix, ns_uri):
        """
        Set the namespace prefix of the :class:`xml4h.nodes.Element` node
        represented by this Builder.

        :return: the current Builder.

        Delegates to :meth:`xml4h.nodes.Element.set_ns_prefix`.
        """
        self._element.set_ns_prefix(prefix, ns_uri)
        return self
