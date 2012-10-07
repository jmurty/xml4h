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

*xml4h* aims to provide a simple and intuitive API for traversing and
manipulating the XML DOM. To that end it includes a number of convenience
methods for performing common tasks:

- Get the :class:`~xml4h.nodes.Document` or root :class:`~xml4h.nodes.Element`
  from any node via the ``document`` and ``root`` attributes respectively.
- You can get the ``name`` attribute of nodes that have a name, or look up
  the different name components with ``prefix`` to get the namespace prefix
  (if any) and ``local_name`` to get the name portion without the prefix.
- Nodes that have a value return it from the ``value`` attribute.
- A node's ``parent`` attribute returns its parent, while the ``ancestors``
  attribute returns a list containing its parent, grand-parent,
  great-grand-parent etc.
- A node's ``children`` attribute returns the child nodes that belong to it,
  while the ``siblings`` attribute returns all other nodes that belong to its
  parent. You can also get the ``siblings_before`` or ``siblings_after`` the
  current node.
- Look up a node's inherited namespace with ``namespace_uri`` or the alias
  ``ns_uri``, or look up its explicitly defined namespace with
  ``current_namespace_uri``.
- Check what type of :class:`~xml4h.nodes.Node` you have with Boolean
  attributes like ``is_element``, ``is_text``, ``is_entity`` etc.


Searching with Find and XPath
-----------------------------

- find
- find_first
- find_doc
- xpath


Filtering Node Lists
--------------------

Many *xml4h* node attributes return a list of nodes as a
:class:`~xml4h.nodes.NodeList` object which confers some special filtering
powers.  You get this special node list object from attributes like
``children``, ``ancestors``, and ``siblings``. Here are some examples of
how you can easily filter a :class:`~xml4h.nodes.NodeList` to get just the
nodes you need:

- Get the first child node using the ``filter`` method::

      >>> # Parse an example XML document about Monty Python films
      >>> doc = xml4h.parse('tests/data/monty_python_films.xml')
      >>> root = doc.MontyPythonFilms

      >>> # Filter to get just the first child
      >>> root.children.filter(first_only=True)
      <xml4h.nodes.Element: "Film">

      >>> # The document has 7 <Film> element children of the root
      >>> len(root.children)
      7

- Get the first child node by treating ``children`` as a callable::

      >>> root.children(first_only=True)
      <xml4h.nodes.Element: "Film">

  When you treat the node list as a callable it calls the ``filter`` method
  behind the scenes, but since doing it the callable way is quicker and
  clearer in code we will use that approach from now on.

- Get the first child node with the ``first`` filtering method, which accepts
  the same constraints as the ``filter`` method::

      >>> root.children.first()
      <xml4h.nodes.Element: "Film">

      >>> # Apply filtering with first
      >>> print root.children.first('WrongName')
      None


- Filter the node list by name::

      >>> for n in root.children('Film'):
      ...     print n.Title.text
      And Now for Something Completely Different
      Monty Python and the Holy Grail
      Monty Python's Life of Brian
      Monty Python Live at the Hollywood Bowl
      Monty Python's The Meaning of Life
      Monty Python: Almost the Truth (The Lawyer's Cut)
      A Liar's Autobiography: Volume IV

      >>> len(root.children('WrongName'))
      0

  .. note::
     Passing a node name as the first argument will match the *local* name of
     a node. You can match the full node name, which might include a prefix
     for example, with a call like: ``.children(local_name='SomeName')``.

- Filter with a custom function::

      >>> # Filter to films released in the year 1979
      >>> for n in root.children('Film',
      ...         filter_fn=lambda node: node.attributes['year'] == '1979'):
      ...     print n.Title.text
      Monty Python's Life of Brian


"Magical" Node Traversal
------------------------


:class:`~xml4h.nodes.NodeAttrAndChildElementLookupsMixin`


Manipulating Nodes
------------------

- Set name and value
- delete



Working with Elements
---------------------


