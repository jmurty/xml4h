from .builder import Builder
from .writer import write

from xml4h.impls.xml_dom_minidom import XmlDomImplAdapter
from xml4h.impls.lxml_etree import LXMLAdapter


__title__ = 'xml4h'
__version__ = '0.1.0'


# List of xml4h implementation classes, in order of preference
_IMPLEMENTATION_CLASSES = [LXMLAdapter, XmlDomImplAdapter]

_IMPLEMENTATIONS_AVAILABLE = []
_IMPLEMENTATIONS_UNAVAILABLE = []

for impl_class in _IMPLEMENTATION_CLASSES:
    if impl_class.is_available():
        _IMPLEMENTATIONS_AVAILABLE.append(impl_class)
    else:
        _IMPLEMENTATIONS_UNAVAILABLE.append(impl_class)


best_adapter = _IMPLEMENTATIONS_AVAILABLE[0]


def parse(to_parse, ignore_whitespace_text_nodes=True, adapter=None):
    """
    Return an xml4h document based on an XML DOM parsed from a string or
    file-like input, using the supplied implementation adapter
    (or the xml4h preferred implementation if not supplied).

    Params:
     - `to_parse` : a string containing XML data or a file path. An input
       containing any '<' characters is treated as literal XML data,
       everything else is treated as a file path.
    """
    if adapter is None:
        adapter = best_adapter
    if isinstance(to_parse, basestring) and '<' in to_parse:
        return adapter.parse_string(to_parse, ignore_whitespace_text_nodes)
    else:
        return adapter.parse_file(to_parse, ignore_whitespace_text_nodes)


def builder(root_tagname, ns_uri=None, adapter=None):
    """
    Return a new Builder based on an XML DOM document created with the
    supplied implementation adapter (or the xml4h preferred implementation
    if not supplied).
    """
    if adapter is None:
        adapter = best_adapter
    impl_doc = adapter.create_document(root_tagname, ns_uri=ns_uri)
    return Builder(impl_doc.root)
