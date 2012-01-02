import re

from xml4h.nodes import Node, ElementNode


class XmlDomNode(Node):

    def _new_element_node(self, tagname, namespace_uri=None):
        if namespace_uri is None:
            return self.document.createElement(tagname)
        else:
            return self.document.createElementNS(namespace_uri, tagname)

    def _new_text_node(self, text):
        return self.document.createTextNode(text)

    def _new_comment_node(self, text):
        return self.document.createComment(text)

    def _new_processing_instruction_node(self, target, data):
        return self.document.createProcessingInstruction(target, data)

    def _get_parent(self, element):
        return element.parentNode

    def _get_root_element(self):
        return self.document.firstChild

    def write(self, writer, encoding='utf-8',
            indent=0, newline='\n', omit_declaration=False):
        self.document.write(writer, encoding=encoding,
            indent='', addident=' ' * indent, newl=newline)

    def xml(self, encoding='utf-8',
            indent=4, newline='\n', omit_declaration=False):
        xml = self.document.toprettyxml(encoding=encoding,
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


