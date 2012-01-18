from StringIO import StringIO

def parse_string_xmldom(xml_str, ignore_whitespace_text_nodes=True):
    string_io = StringIO(xml_str)
    return parse_file_xmldom(string_io, ignore_whitespace_text_nodes)

def parse_file_xmldom(xml_file, ignore_whitespace_text_nodes=True):
    from xml.dom.minidom import parse
    impl_doc = parse(xml_file)
    from xml4h.impls.xml_dom import XmlDomImplAdapter
    wrapped_doc = XmlDomImplAdapter.wrap_node(impl_doc)
    if ignore_whitespace_text_nodes:
        _ignore_whitespace_text_nodes(wrapped_doc)
    return wrapped_doc

def _ignore_whitespace_text_nodes(wrapped_node):
    '''
    Find and delete in node and descendents any text nodes that contain
    nothing but whitespace. Useful for cleaning up excess text nodes
    in a document DOM after parsing a pretty-printed XML document.
    '''
    for child in wrapped_node.children:
        if child.is_text and child.value.strip() == '':
            child.delete()
        else:
            _ignore_whitespace_text_nodes(child)
