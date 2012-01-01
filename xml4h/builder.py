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


# TODO Hide this class
class XmlDomBuilderNode(object):
    '''
    Wrap underlying XML document-building libarary/implementation and
    expose utility functions to easily build XML nodes.

    This class wraps the xml.dom module included with Python 2.0+
    '''

    @classmethod
    def create(cls, dom_impl, root_tagname, namespace_uri=None):
        # Construct the Document and root Element
        doctype = None  # TODO
        doc = dom_impl.createDocument(
            namespace_uri, root_tagname, doctype)
        # Automatically add namespace URI to root Element as attribute
        if namespace_uri is not None:
            doc.firstChild.setAttributeNS(
                'http://www.w3.org/2000/xmlns/',
                'xmlns', namespace_uri)
        # Return a node wrapping the root element
        return XmlDomBuilderNode(_element=doc.firstChild, _document=doc)

    def __init__(self, _element=None, _document=None):
        if _document is None or _element is None:
            raise Exception('Cannot instantiate without element and document')
        self._document = _document
        self._element = _element

    @property
    def root(self):
        return XmlDomBuilderNode(_document=self._document,
            _element=self._document.firstChild)

    def __eq__(self, other):
        if self is other:
            return True
        # xml.dom.Document's == test doesn't match equivalent docs
        return unicode(self) == unicode(other)

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

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.xml()

    def up(self, count=1, to_tagname=None):
        elem = self._element
        up_count = 0
        while True:
            # Don't go up beyond the document root
            if elem.parentNode is None or elem.parentNode == self._document:
                return XmlDomBuilderNode(_document=self._document,
                    _element=self._document.firstChild)
            elem = elem.parentNode
            if to_tagname is None:
                up_count += 1
                if up_count >= count:
                    break
            else:
                if elem.nodeName == to_tagname:
                    break
        return XmlDomBuilderNode(_element=elem, _document=self._document)

    def element(self, tagname, namespace_uri=None,
            attributes=None, text=None, before=False):
        if namespace_uri is None:
            elem = self._document.createElement(tagname)
        else:
            elem = self._document.createElementNS(namespace_uri, tagname)
        # Automatically add namespace URI to Element as attribute
        if namespace_uri is not None:
            self._namespace(elem, namespace_uri)
        if attributes is not None:
            self._attributes(elem, attr_obj=attributes)
        if text is not None:
            self._text(elem, text=text)
        if before:
            self._element.parentNode.insertBefore(elem, self._element)
        else:
            self._element.appendChild(elem)
        return XmlDomBuilderNode(_element=elem, _document=self._document)

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
            if namespace_uri is None:
                element.setAttribute(n, v)
            else:
                element.setAttributeNS(namespace_uri, n, v)

    def attributes(self, attr_obj=None, namespace_uri=None, **attr_dict):
        self._attributes(self._element,
            attr_obj=attr_obj, namespace_uri=namespace_uri, **attr_dict)
        return self

    attrs = attributes  # Alias

    a = attributes  # Alias

    def _text(self, element, text):
        text_node = self._document.createTextNode(text)
        element.appendChild(text_node)

    def text(self, text):
        self._text(self._element, text)
        return self

    t = text  # Alias

    def _comment(self, element, text):
        comment_node = self._document.createComment(text)
        element.appendChild(comment_node)

    def comment(self, text):
        self._comment(self._element, text)
        return self

    c = comment  # Alias

    def _instruction(self, element, target, data):
        instruction_node = self._document.createProcessingInstruction(
            target, data)
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

# TODO
#    def _cdata(self, dlement, data):
#        cdata_node = self._document.createCDATANode(data)
#        element.appendChild(cdata_node)
#
#    def cdata(self, data):
#        self._cdata(self._element, data)
#        return self
#
#    data = cdata  # Alias
#
#    d = cdata  # Alias
