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

    def up(self, count=1):
        elem = self._element
        for i in range(count):
            # Don't try to go up beyond the document root
            if elem.parentNode is None or elem.parentNode == self._document:
                return XmlDomBuilderNode(_document=self._document,
                    _element=self._document.firstChild)
            elem = elem.parentNode
        return XmlDomBuilderNode(_element=elem, _document=self._document)

    def element(self, tagname, namespace_uri=None):
        if namespace_uri is None:
            elem = self._document.createElement(tagname)
        else:
            elem = self._document.createElementNS(namespace_uri, tagname)
        self._element.appendChild(elem)
        return XmlDomBuilderNode(_element=elem, _document=self._document)

    elem = element  # Alias

    e = element  # Alias

    def attributes(self, attr_obj=None, namespace_uri=None, **attr_dict):
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
                self._element.setAttribute(n, v)
            else:
                self._element.setAttributeNS(namespace_uri, n, v)
        return self

    attrs = attributes  # Alias

    a = attributes  # Alias

    def text(self, text):
        text_node = self._document.createTextNode(text)
        self._element.appendChild(text_node)
        return self

    t = text  # Alias
