
def builder(root_tagname, namespace_uri=None):
    # Default builder
    return builder_xmldom(root_tagname, namespace_uri, impl_name='minidom')

def builder_xmldom(root_tagname, namespace_uri=None,
        impl_name=None, impl_features=None):
    import xml.dom
    from xml4h.nodes.impls import XmlDomElementNode
    if impl_features is None:
        impl_features = []
    dom_impl = xml.dom.getDOMImplementation(impl_name, impl_features)
    return XmlDomElementNode.create(
        dom_impl, root_tagname, namespace_uri=namespace_uri)

