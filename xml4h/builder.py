
def builder(root_tagname, ns_uri=None):
    # Default builder
    return builder_xmldom(root_tagname, ns_uri, impl_name='minidom')

def builder_xmldom(root_tagname, ns_uri=None,
        impl_name=None, impl_features=None):
    from xml4h.impls.xml_dom import XmlDomImplWrapper
    return XmlDomImplWrapper.create_document(root_tagname,
        ns_uri=ns_uri, impl_name=None, impl_features=None)

