=========
DOM Nodes
=========

*xml4h* provides node objects and convenience methods that make it easier to
work with an in-memory XML document object model (DOM) produced by parsing an
existing document or building a new one.

For API-level documentation about *xml4h* nodes see :ref:`api-nodes`.


What is an *xml4h* Node?
------------------------

To best understand what an *xml4h* node is, you should know what it isn't.
*xml4h* is not a fully-fledged XML library in its own right, instead it sits
on top of an underlying :ref:`XML library implementation <xml-lib-adapters>`
and provides an improved API and tool suite.

This means that an *xml4h* node is really a decorator or wrapper of a node
(or similar) object provided by an underlying XML library, such as *lxml*'s
``lxml.etree._Element`` or the *minidom*'s ``xml.dom.minidom.Element``. The
work done by *xml4h*'s :class:`~xml4h.nodes.Node` and its subclasses is to
mediate your interactions with the underlying XML implementation, whatever
that implementation is.


Wrapping and Unwrapping *xml4h* Nodes
-------------------------------------

You can easily convert to or from *xml4h*'s wrapped version of an
implementation node. For example, if you prefer the *lxml* library's
`ElementMaker <http://lxml.de/tutorial.html#the-e-factory>`_ document builder
approach to the :ref:`xml4h Builder <builder>`, you can create a document
in *lxml*...::

    >>> from lxml.builder import ElementMaker
    >>> E = ElementMaker()
    >>> lxml_doc = E.DocRoot(
    ...     E.Item(
    ...         E.Name('Item 1'),
    ...         E.Value('Value 1')
    ...     ),
    ...     E.Item(
    ...         E.Name('Item 2'),
    ...         E.Value('Value 2')
    ...     )
    ... )
    >>> lxml_doc  # doctest:+ELLIPSIS
    <Element DocRoot at ...

...and then convert (or, more accurately, wrap) the *lxml* nodes to make them
*xml4h* versions::

    >>> import xml4h

    >>> # Convert lxml Document to xml4h version
    >>> xml4h_doc = xml4h.LXMLAdapter.wrap_document(lxml_doc)
    >>> xml4h_doc.children
    [<xml4h.nodes.Element: "Item">, <xml4h.nodes.Element: "Item">]

    >>> # Get an element within the lxml document
    >>> lxml_elem = list(lxml_doc)[0]
    >>> lxml_elem  # doctest:+ELLIPSIS
    <Element Item at ...

    >>> # Convert lxml Element to xml4h version
    >>> xml4h_elem = xml4h.LXMLAdapter.wrap_node(lxml_elem, lxml_doc)
    >>> xml4h_elem  # doctest:+ELLIPSIS
    <xml4h.nodes.Element: "Item">

You can reach the underlying XML implementation document or node at any time
from an *xml4h* node::

    >>> # Get an xml4h node's underlying implementation node
    >>> xml4h_elem.impl_node  # doctest:+ELLIPSIS
    <Element Item at ...
    >>> xml4h_elem.impl_node == lxml_elem
    True

    >>> # Get the underlying implementatation document from any node
    >>> xml4h_elem.impl_document  # doctest:+ELLIPSIS
    <Element DocRoot at ...
    >>> xml4h_elem.impl_document == lxml_doc
    True


Traversing Nodes
----------------


Working with Elements
---------------------


Namespaces
----------


