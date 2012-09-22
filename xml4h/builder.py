"""
Builder is a utility class that makes it easy to create valid, well-formed
XML documents using relatively sparse python code.  The builder class works
by wrapping an ``xml4h.nodes.Element`` node to provide "chainable" methods
focussed specifically on adding XML content.

Each method that adds content returns a Builder instance representing the
current or the newly-added Element. Behind the scenes, the builder uses the
``xml4h`` node traversal and manipulation methods to add content directly
to the underlying DOM.

You will not generally create Builder instances directly, but will instead
call the ``xml4h.builder`` method with an existing Element node or the name
for a new root element.
"""
import xml4h


class Builder(object):
    """
    Builder class that wraps an ``xml4h.nodes.Element`` node with methods
    for adding XML content to an underlying DOM.
    """

    def __init__(self, element):
        """
        Create a Builder representing an xml4h Element node.

        :param element: Element node to represent
        :type element: xml4h.nodes.Element
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
        Return the ``xml4h.nodes.Element`` node represented by this Builder.
        """
        return self._element

    @property
    def document(self):
        """
        Return the ``xml4h.nodes.Document`` node that contains the Element
        represented by this Builder.
        """
        return self._element.document

    @property
    def root(self):
        """Return the ``xml4h.nodes.Element`` root node ancestor of the
        Element represented by this Builder"""
        return self._element.root

    def find(self, **kwargs):
        """
        Return a list of ``xml4h.nodes.Element`` node descendants of the
        Element represented by this builder that match the given constraints.

        Delegates to :meth:`xml4h.nodes.Node.find`
        """
        return self._element.find(**kwargs)

    def find_doc(self, **kwargs):
        """
        Return a list of ``xml4h.nodes.Element`` nodes in this Element's
        owning Document that match the given constraints.

        Delegates to :meth:`xml4h.nodes.Node.doc_find`.
        """
        return self._element.find_doc(**kwargs)

    def write(self, *args, **kwargs):
        """
        Write XML text for the Element represented by this builder.

        Delegates to :meth:`xml4h.nodes.Node.write`.
        """
        self.dom_element.write(*args, **kwargs)

    def write_doc(self, *args, **kwargs):
        """
        Write XML text for the Document containing the Element
        represented by this builder.

        Delegates to :meth:`xml4h.nodes.Node.doc_write`.
        """
        self.dom_element.doc_write(*args, **kwargs)

    def up(self, count=1, to_name=None):
        """
        Return a builder representing an ancestor of the current Element,
        by default the parent Element.

        :param count: return the n'th ancestor element; defaults to 1 which
                      means the immediate parent. If *count* is greater than
                      the number of number of ancestors return the document's
                      root element.
        :type count: integer, 1 or greater
        :param to_name: return the nearest ancestor element with the matching
                      name, or the document's root element if there are no
                      matching elements.
        :type to_name: string
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

    def element(self, name, ns_uri=None, prefix=None,
            attributes=None, text=None, before_this_element=False):
        """
        Add a child element to the Element node anchoring the current
        Builder and return a new Builder anchored to that child element.
        """
        child_element = self._element.add_element(
            name, ns_uri=ns_uri, prefix=prefix,
            attributes=attributes, text=text,
            before_this_element=before_this_element)
        return Builder(child_element)

    elem = element  # Alias

    e = element  # Alias

    def attributes(self, attr_obj=None, ns_uri=None, **attr_dict):
        """
        Add one or more attributes to the Element node anchoring the current
        Builder and return the current Builder.
        """
        self._element.set_attributes(
            attr_obj=attr_obj, ns_uri=ns_uri, **attr_dict)
        return self

    attrs = attributes  # Alias

    a = attributes  # Alias

    def text(self, text):
        """
        Add a text node to the Element node anchoring the current
        Builder and return the current Builder.
        """
        self._element.add_text(unicode(text))
        return self

    t = text  # Alias

    def comment(self, text):
        """
        Add a comment node to the Element node anchoring the current
        Builder and return the current Builder.
        """
        self._element.add_comment(text)
        return self

    c = comment  # Alias

    def processing_instruction(self, target, data):
        """
        Add a processing instruction node to the Element node anchoring
        the current Builder and return the current Builder.
        """
        self._element.add_instruction(target, data)
        return self

    instruction = processing_instruction  # Alias

    i = instruction  # Alias

    def cdata(self, text):
        """
        Add a CDATA node to the Element node anchoring the current
        Builder and return the current Builder.
        """
        self._element.add_cdata(text)
        return self

    data = cdata  # Alias

    d = cdata  # Alias

    def ns_prefix(self, prefix, ns_uri):
        """
        Set namespace prefix of Element node anchoring the current Builder
        """
        self._element.set_ns_prefix(prefix, ns_uri)
        return self
