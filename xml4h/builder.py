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
                "Builder can only be created with an %s.%s instance"
                % (xml4h.nodes.Element.__module__,
                   xml4h.nodes.Element.__name__))
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
        Write XML text for the element represented by this builder.

        Delegates to :meth:`xml4h.nodes.Node.write`.
        """
        self.dom_element.write(*args, **kwargs)

    def write_doc(self, *args, **kwargs):
        """
        Write XML text for the Document containing the element
        represented by this builder.

        Delegates to :meth:`xml4h.nodes.Node.write_doc`.
        """
        self.dom_element.write_doc(*args, **kwargs)

    def up(self, count=1, to_name=None):
        """
        :return: a builder representing an ancestor of the current element,
                 by default the parent element.

        :param count: return the n'th ancestor element; defaults to 1 which
            means the immediate parent. If *count* is greater than the number
            of number of ancestors return the document's root element.
        :type count: integer >= 1 or None
        :param to_name: return the nearest ancestor element with the matching
            name, or the document's root element if there are no matching
            elements. This argument trumps the ``count`` argument.
        :type to_name: string or None
        """
        elem = self._element
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if elem.is_root or elem.parent is None:
                break
            elem = elem.parent
            if to_name is None:
                up_count += 1
                if up_count >= count:
                    break
            else:
                if elem.name == to_name:
                    break
        return Builder(elem)

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
