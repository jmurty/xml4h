
def parse_string_xmldom(xml_str):
    from xml.dom.minidom import parseString
    impl_doc = parseString(xml_str)
    from xml4h.impls.xml_dom import XmlDomImplAdapter
    return XmlDomImplAdapter.wrap_node(impl_doc)

def parse_file_xmldom(xml_file):
    from xml.dom.minidom import parse
    impl_doc = parse(xml_file)
    from xml4h.impls.xml_dom import XmlDomImplAdapter
    return XmlDomImplAdapter.wrap_node(impl_doc)
