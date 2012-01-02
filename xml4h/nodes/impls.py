import re
from StringIO import StringIO

from xml4h import is_pyxml_installed
from xml4h.nodes import Node, ElementNode


class XmlDomNode(Node):

    def _new_element_node(self, tagname, namespace_uri=None):
        if namespace_uri is None:
            return self.impl_document.createElement(tagname)
        else:
            return self.impl_document.createElementNS(namespace_uri, tagname)

    def _new_text_node(self, text):
        return self.impl_document.createTextNode(text)

    def _new_comment_node(self, text):
        return self.impl_document.createComment(text)

    def _new_processing_instruction_node(self, target, data):
        return self.impl_document.createProcessingInstruction(target, data)

    def _get_parent(self, element):
        return element.parentNode

    def _get_root_element(self):
        return self.impl_document.firstChild

    def write(self, writer, encoding='utf-8',
            indent=0, newline='\n', omit_declaration=False):
        self.impl_document.write(writer, encoding=encoding,
            indent='', addident=' ' * indent, newl=newline)

    # Reference: stackoverflow.com/questions/749796/pretty-printing-xml-in-python
    def xml(self, encoding='utf-8',
            indent=4, newline='\n', omit_declaration=False):
        if is_pyxml_installed():
            # Use PyXML's pretty-printer that doesn't add whitespace
            # around text nodes
            from xml.dom.ext import PrettyPrint
            string_io = StringIO()
            # TODO Possible to set newlines?
            if newline != '\n':
                raise Exception('newline parameter is not supported by PyXML')
            PrettyPrint(self.impl_document, stream=string_io,
                encoding=encoding, indent=' ' * indent)
            xml = string_io.getvalue()
        else:
            xml = self.impl_document.toprettyxml(encoding=encoding,
                indent=' ' * indent, newl=newline)
        if omit_declaration:
            return re.sub(r'^<\?.*\?>\s*', '', xml, flags=re.MULTILINE)
        return xml


class XmlDomElementNode(XmlDomNode, ElementNode):
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
        builder = cls(doc.firstChild, doc)
        # Automatically add namespace URI to root Element as attribute
        if namespace_uri is not None:
            builder._set_attribute(doc.firstChild, 'xmlns', namespace_uri,
                namespace_uri='http://www.w3.org/2000/xmlns/')
        return builder

    def _add_child_node(self, parent, child, before_sibling=None):
        if before_sibling is not None:
            parent.insertBefore(child, before_sibling)
        else:
            parent.appendChild(child)

    def _set_attribute(self, element, name, value, namespace_uri=None):
        if namespace_uri is not None:
            element.setAttributeNS(namespace_uri, name, value)
        else:
            element.setAttribute(name, value)

    def _get_tagname(self, element):
        return element.nodeName

    def __eq__(self, other):
        if super(XmlDomElementNode, self).__eq__(other):
            return True
        # xml.dom.Document's == test doesn't match equivalent docs
        return unicode(self) == unicode(other)


