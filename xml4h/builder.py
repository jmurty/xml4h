import xml.dom
import re


def builder(root_tagname, namespace_uri=None):
    # Default builder
    return builder_xmldom(root_tagname, namespace_uri, impl_name='minidom')

def builder_xmldom(root_tagname, namespace_uri=None,
        impl_name=None, impl_features=None):
    if impl_features is None:
        impl_features = []
    dom_impl = xml.dom.getDOMImplementation(impl_name, impl_features)
    return XmlDomBuilderNode.create(
        dom_impl, root_tagname, namespace_uri=namespace_uri)


# TODO Hide everything below here


class XmlBuilderNode(object):
    '''
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.
    '''

    @classmethod
    def create(cls, root_tagname, namespace_uri=None):
        raise NotImplementedError()

    def _create_element(self, tagname, namespace_uri):
        raise NotImplementedError()

    def _create_text_node(self, text):
        raise NotImplementedError()

    def _create_comment(self, text):
        raise NotImplementedError()

    def _create_processing_instruction(self, target, data):
        raise NotImplementedError()

    def _create_cdata(self, text):
        raise NotImplementedError()

    def _append_child(self, parent, child):
        raise NotImplementedError()

    def _prepend_child(self, parent, child, sibling):
        raise NotImplementedError()

    def _get_root_element(self):
        raise NotImplementedError()

    def _get_element_parent(self, element):
        raise NotImplementedError()

    def _get_element_tagname(self, element):
        raise NotImplementedError()

    def _set_attribute(self, element, name, value, namespace_uri=None):
        raise NotImplementedError()

    def write(self, writer, encoding='utf-8',
            indent=0, newline='\n', omit_declaration=False):
        raise NotImplementedError()

    def xml(self, encoding='utf-8',
            indent=4, newline='\n', omit_declaration=False):
        raise NotImplementedError()


    def __init__(self, _element=None, _document=None):
        if _document is None or _element is None:
            raise Exception('Cannot instantiate without element and document')
        self._document = _document
        self._element = _element

    def __eq__(self, other):
        if self is other:
            return True
        return self._document == getattr(other, '_document')

    @property
    def klass(self):
        return self.__class__

    @property
    def root(self):
        return self.klass(_document=self._document,
            _element=self._get_root_element())

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.xml()

    def up(self, count=1, to_tagname=None):
        elem = self._element
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if (self._get_element_parent(elem) is None
                    or self._get_element_parent(elem) == self._document):
                return self.klass(_document=self._document,
                    _element=self._get_root_element())
            elem = self._get_element_parent(elem)
            if to_tagname is None:
                up_count += 1
                if up_count >= count:
                    break
            else:
                if self._get_element_tagname(elem) == to_tagname:
                    break
        return self.klass(_element=elem, _document=self._document)

    def element(self, tagname, namespace_uri=None,
            attributes=None, text=None, before=False):
        elem = self._create_element(tagname, namespace_uri)
        # Automatically add namespace URI to Element as attribute
        if namespace_uri is not None:
            self._namespace(elem, namespace_uri)
        if attributes is not None:
            self._attributes(elem, attr_obj=attributes)
        if text is not None:
            self._text(elem, text=text)
        if before:
            self._prepend_child(
                self._get_element_parent(self._element), elem, self._element)
        else:
            self._append_child(self._element, elem)
        return self.klass(_element=elem, _document=self._document)

    elem = element  # Alias

    e = element  # Alias

    def _attributes(self, element,
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

    def attributes(self, attr_obj=None, namespace_uri=None, **attr_dict):
        self._attributes(self._element,
            attr_obj=attr_obj, namespace_uri=namespace_uri, **attr_dict)
        return self

    attrs = attributes  # Alias

    a = attributes  # Alias

    def _text(self, element, text):
        text_node = self._create_text_node(text)
        element.appendChild(text_node)

    def text(self, text):
        self._text(self._element, text)
        return self

    t = text  # Alias

    def _comment(self, element, text):
        comment_node = self._create_comment(text)
        element.appendChild(comment_node)

    def comment(self, text):
        self._comment(self._element, text)
        return self

    c = comment  # Alias

    def _instruction(self, element, target, data):
        instruction_node = self._create_processing_instruction(target, data)
        element.appendChild(instruction_node)

    def instruction(self, target, data):
        self._instruction(self._element, target, data)
        return self

    processing_instruction = instruction  # Alias

    i = instruction  # Alias

    def _namespace(self, element, namespace_uri, prefix=None):
        if not prefix:
            ns_name = 'xmlns'
        else:
            ns_name = 'xmlns:%s' % prefix
        self._attributes(element,
            {ns_name: namespace_uri},
            namespace_uri='http://www.w3.org/2000/xmlns/')

    def namespace(self, namespace_uri, prefix=None):
        self._namespace(self._element, namespace_uri, prefix=prefix)
        return self

    ns = namespace  # Alias

    def _cdata(self, dlement, data):
        cdata_node = self._create_cdata(data)
        element.appendChild(cdata_node)

    def cdata(self, data):
        self._cdata(self._element, data)
        return self

    data = cdata  # Alias

    d = cdata  # Alias


class XmlDomBuilderNode(XmlBuilderNode):
    '''
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.

    This class wraps the xml.dom module included with Python 2.0+
    '''

    @classmethod
    def create(cls, dom_impl, root_tagname, namespace_uri=None):
        doctype = None  # TODO
        doc = dom_impl.createDocument(
            namespace_uri, root_tagname, doctype)
        builder = cls(_element=doc.firstChild, _document=doc)
        # Automatically add namespace URI to root Element as attribute
        if namespace_uri is not None:
            builder._set_attribute(doc.firstChild, 'xmlns', namespace_uri,
                namespace_uri='http://www.w3.org/2000/xmlns/')
        return builder

    def _create_element(self, tagname, namespace_uri=None):
        if namespace_uri is None:
            return self._document.createElement(tagname)
        else:
            return self._document.createElementNS(namespace_uri, tagname)

    def _create_text_node(self, text):
        return self._document.createTextNode(text)

    def _create_comment(self, text):
        return self._document.createComment(text)

    def _create_processing_instruction(self, target, data):
        return self._document.createProcessingInstruction(target, data)

    def _append_child(self, parent, child):
        parent.appendChild(child)

    def _prepend_child(self, parent, child, sibling):
        parent.insertBefore(child, sibling)

    def _set_attribute(self, element, name, value, namespace_uri=None):
        if namespace_uri is not None:
            element.setAttributeNS(namespace_uri, name, value)
        else:
            element.setAttribute(name, value)

    def _get_root_element(self):
        return self._document.firstChild

    def _get_element_parent(self, element):
        return element.parentNode

    def _get_element_tagname(self, element):
        return element.nodeName

    def write(self, writer, encoding='utf-8',
            indent=0, newline='\n', omit_declaration=False):
        self._document.write(writer, encoding=encoding,
            indent='', addident=' ' * indent, newl=newline)

    def xml(self, encoding='utf-8',
            indent=4, newline='\n', omit_declaration=False):
        xml = self._document.toprettyxml(encoding=encoding,
            indent=' ' * indent, newl=newline)
        if omit_declaration:
            return re.sub(r'^<\?.*\?>\s*', '', xml, flags=re.MULTILINE)
        return xml

    def __eq__(self, other):
        if super(XmlDomBuilderNode, self).__eq__(other):
            return True
        # xml.dom.Document's == test doesn't match equivalent docs
        return unicode(self) == unicode(other)
