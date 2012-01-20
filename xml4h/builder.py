
def builder(root_tagname, ns_uri=None):
    # Default builder
    return builder_xmldom(root_tagname, ns_uri, impl_name='minidom')

def builder_xmldom(root_tagname, ns_uri=None,
        impl_name=None, impl_features=None):
    from xml4h.impls.xml_dom import XmlDomImplAdapter
    wrapped_doc = XmlDomImplAdapter.create_document(root_tagname,
        ns_uri=ns_uri, impl_name=None, impl_features=None)
    return wrapped_doc.root

def builder_lxml(root_tagname, ns_uri=None):
    from xml4h.impls.lxml_etree import LXMLAdapter
    wrapped_doc = LXMLAdapter.create_document(
        root_tagname, ns_uri=ns_uri)
    return wrapped_doc.root

