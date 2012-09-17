from xml4h.nodes import Element


class Builder(object):
    """
    Builder with convenience methods to construct an XML DOM using chained
    methods.
    """

    def __init__(self, element):
        """Create a Builder anchored to an xml4h Element node"""
        if not isinstance(element, Element):
            raise ValueError(
                "Builder can only be created with an %s.%s instance"
                % (Element.__module__, Element.__name__))
        self._element = element

    @property
    def doc_element(self):
        """Return the xml4h Element node that anchors this Builder"""
        return self._element

    @property
    def document(self):
        """
        Return the root xml4h Document of the document containing the node
        than anchors this Builder.
        """
        return self._element.document

    @property
    def root(self):
        """Return the root of the Element node that anchors this Builder"""
        return self._element.root

    def find(self, **kwargs):
        """
        Return a list of Element node descendents of this node that match
        the given constraints.
        """
        return self._element.find(**kwargs)

    def doc_find(self, **kwargs):
        """
        Return a list of all Element nodes in the document that match
        the given constraints.
        """
        return self._element.doc_find(**kwargs)

    def up(self, count=1, to_tagname=None):
        """
        Return a Builder anchored on an element node that is either:
        - `count` elements towards the document root, or
        - has a tag name matching the given `to_tagname`

        Will return a Builder anchored to the document's root node if
        the `count` exceeds the number of ancestors between the current
        element and the document root, or if no ancestor node tag name
        matches `to_tagname`.
        """
        elem = self._element
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if elem.is_root or elem.parent is None:
                break
            elem = elem.parent
            if to_tagname is None:
                up_count += 1
                if up_count >= count:
                    break
            else:
                if elem.name == to_tagname:
                    break
        return Builder(elem)

    def element(self, tagname, ns_uri=None, prefix=None,
            attributes=None, text=None, before_this_element=False):
        """
        Add a child element to the Element node anchoring the current
        Builder and return a new Builder anchored to that child element.
        """
        child_element = self._element.add_element(
            tagname, ns_uri=ns_uri, prefix=prefix,
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
        self._element.add_text(text)
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

    def instruction(self, target, data):
        """
        Add a processing instruction node to the Element node anchoring
        the current Builder and return the current Builder.
        """
        self._element.add_instruction(target, data)
        return self

    processing_instruction = instruction  # Alias

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
