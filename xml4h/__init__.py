import six

import xml4h

# Make commonly-used classes and functions available in xml4h module
from xml4h.impls.xml_dom_minidom import XmlDomImplAdapter
from xml4h.impls.xml_etree_elementtree import (
    ElementTreeAdapter, cElementTreeAdapter)
from xml4h.impls.lxml_etree import LXMLAdapter
from xml4h.builder import Builder
from xml4h.writer import write_node


__title__ = 'xml4h'
__version__ = '1.0'


# List of xml4h adapter classes, in order of preference
_ADAPTER_CLASSES = [
    LXMLAdapter,
    cElementTreeAdapter,
    ElementTreeAdapter,
    XmlDomImplAdapter]

_ADAPTERS_AVAILABLE = []
_ADAPTERS_UNAVAILABLE = []

for impl_class in _ADAPTER_CLASSES:
    if impl_class.is_available():
        _ADAPTERS_AVAILABLE.append(impl_class)
    else:
        _ADAPTERS_UNAVAILABLE.append(impl_class)


best_adapter = _ADAPTERS_AVAILABLE[0]
"""
The :ref:`best adapter available <best-adapter>` in the Python environment.
This adapter is the default when parsing or creating XML documents,
unless overridden by passing a specific adapter class.
"""


def parse(
    to_parse, ignore_whitespace_text_nodes=True, adapter=None
):
    """
    Parse an XML document into an *xml4h*-wrapped DOM representation
    using an underlying XML library implementation.

    :param to_parse: an XML document file, document bytes, or the
        path to an XML file. If a bytes value is given that contains
        a ``<`` character it is treated as literal XML data, otherwise
        a bytes value is treated as a file path.
    :type to_parse: a file-like object or string
    :param bool ignore_whitespace_text_nodes: if ``True`` pure whitespace
        nodes are stripped from the parsed document, since these are
        usually noise introduced by XML docs serialized to be human-friendly.
    :param adapter: the *xml4h* implementation adapter class used to parse
        the document and to interact with the resulting nodes.
        If None, :attr:`best_adapter` will be used.
    :type adapter: adapter class or None

    :return: an :class:`xml4h.nodes.Document` node representing the
        parsed document.

    Delegates to an adapter's :meth:`~xml4h.impls.interface.parse_string` or
    :meth:`~xml4h.impls.interface.parse_file` implementation.
    """
    if adapter is None:
        adapter = best_adapter
    if isinstance(to_parse, six.binary_type) and b'<' in to_parse:
        return adapter.parse_bytes(to_parse, ignore_whitespace_text_nodes)
    elif isinstance(to_parse, six.string_types) and '<' in to_parse:
        return adapter.parse_string(to_parse, ignore_whitespace_text_nodes)
    else:
        return adapter.parse_file(to_parse, ignore_whitespace_text_nodes)


def build(tagname_or_element, ns_uri=None, adapter=None):
    """
    Return a :class:`~xml4h.builder.Builder` that represents an element in
    a new or existing XML DOM and provides "chainable" methods focussed
    specifically on adding XML content.

    :param tagname_or_element: a string name for the root node of a
        new XML document, or an :class:`~xml4h.nodes.Element` node in an
        existing document.
    :type tagname_or_element: string or :class:`~xml4h.nodes.Element` node
    :param ns_uri: a namespace URI to apply to the new root node. This
        argument has no effect this method is acting on an element.
    :type ns_uri: string or None
    :param adapter: the *xml4h* implementation adapter class used to
        interact with the document DOM nodes.
        If None, :attr:`best_adapter` will be used.
    :type adapter: adapter class or None

    :return: a :class:`~xml4h.builder.Builder` instance that represents an
        :class:`~xml4h.nodes.Element` node in an XML DOM.
    """
    if adapter is None:
        adapter = best_adapter
    if isinstance(tagname_or_element, six.string_types):
        doc = adapter.create_document(
            tagname_or_element, ns_uri=ns_uri)
        element = doc.root
    elif isinstance(tagname_or_element, xml4h.nodes.Element):
        element = tagname_or_element
    else:
        raise xml4h.exceptions.IncorrectArgumentTypeException(
            tagname_or_element, [str, xml4h.nodes.Element])
    return Builder(element)
