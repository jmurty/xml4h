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
that implementation is. See the section :ref:`wrap-unwrap-nodes` for more
information about converting to and from *xml4h* nodes.


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

There are two ways to search for elements within an *xml4h* document: find and
xpath.

The find methods provided by the library are easy to use but can only perform
relatively simple searches that return :class:`~xml4h.nodes.Element` results,
whereas you need to be familiar with XPath query syntax to search effectively
with the ``xpath`` method but you can perform more complex searches and get
results other than just elements.

Below are some examples of both kinds of search, but first we need to load
an example document to search::

      >>> # Parse an example XML document about Monty Python films
      >>> import xml4h
      >>> doc = xml4h.parse('tests/data/monty_python_films.xml')

Find Methods
............

*xml4h* provides three different find methods:

- :meth:`~xml4h.nodes.Node.find` searches descendants of the current node for
  elements matching the given constraints. You can search by element name,
  by namespace URI, or even with no constraints at all::

      >>> # Find ALL elements in the document
      >>> elems = doc.find()
      >>> [e.name for e in elems]  # doctest:+ELLIPSIS
      ['MontyPythonFilms', 'Film', 'Title', 'Description', 'Film', 'Title', 'Description',...

      >>> # Find the seven <Film> elements in the XML document
      >>> film_elems = doc.find('Film')
      >>> [e.Title.text for e in film_elems]  # doctest:+ELLIPSIS
      ['And Now for Something Completely Different', 'Monty Python and the Holy Grail',...

  Note that the :meth:`~xml4h.nodes.Node.find` method only finds descendants
  of the node you run it on::

      >>> # Find <Title> elements in a single <Film> element; there's only one
      >>> film_elem = doc.find('Film', first_only=True)
      >>> film_elem.find('Title')
      [<xml4h.nodes.Element: "Title">]

- :meth:`~xml4h.nodes.Node.find_first` searches descendants of the current
  node but only returns the first result element, not a list. If there are no
  matching element results this method returns *None*::

      >>> # Find the first <Film> element in the document
      >>> doc.find_first('Film')
      <xml4h.nodes.Element: "Film">

      >>> # Search for an element that does not exist
      >>> print doc.find_first('OopsWrongName')
      None

  If you were paying attention you may have noticed in the example above that
  you can make the :meth:`~xml4h.nodes.Node.find` method do exactly same thing
  as :meth:`~xml4h.nodes.Node.find_first` by passing the keyword argument
  ``first_only=True``.

- :meth:`~xml4h.nodes.Node.find_doc` is a convenience method that searches the
  entire document no matter which node you run it on::

      >>> # Normal find only searches descendants of the current node
      >>> len(film_elem.find('Title'))
      1

      >>> # find_doc searches the entire document
      >>> len(film_elem.find_doc('Title'))
      7

  This method is exactly like calling ``xml4h_node.document.find()``, which is
  actually what happens behind the scenes.

XPath Querying
..............

*xml4h* provides a single XPath search method which is available on
:class:`~xml4h.nodes.Document` and :class:`~xml4h.nodes.Element` nodes:

- :meth:`~xml4h.nodes.XPathMixin.xpath` takes an XPath query string and returns
  the result which may be a list of elements, a list of attributes, a list of
  values, or a single value. The result depends entirely on the kind of query
  you perform.

  XPath queries are well beyond the scope of this documentation but here are
  some examples like the find queries we saw above, and some more complex
  queries::

      >>> # Query for ALL elements in the document
      >>> elems = doc.xpath('//*')  # doctest:+ELLIPSIS
      >>> [e.name for e in elems]  # doctest:+ELLIPSIS
      ['MontyPythonFilms', 'Film', 'Title', 'Description', 'Film', 'Title', 'Description',...

      >>> # Query for the seven <Film> elements in the XML document
      >>> film_elems = doc.xpath('//Film')
      >>> [e.Title.text for e in film_elems]  # doctest:+ELLIPSIS
      ['And Now for Something Completely Different', 'Monty Python and the Holy Grail',...

      >>> # Query for the first <Film> element in the document (returns list)
      >>> doc.xpath('//Film[1]')
      [<xml4h.nodes.Element: "Film">]

      >>> # Query for <Title> elements in a single <Film> element; there's only one
      >>> film_elem = doc.xpath('Film[1]')[0]
      >>> film_elem.xpath('Title')
      [<xml4h.nodes.Element: "Title">]

      >>> # Query for all year attributes
      >>> doc.xpath('//@year')
      ['1971', '1974', '1979', '1982', '1983', '2009', '2012']

      >>> # Query for the title of the film released in 1982
      >>> doc.xpath('//Film[@year="1982"]/Title/text()')
      ['Monty Python Live at the Hollywood Bowl']

.. note::
   XPath querying is currently only available through the *lxml* implementation
   library, so you must have that library installed to use
   :meth:`~xml4h.nodes.XPathMixin.xpath`. You can check whether the XPath
   feature is available with :meth:`~xml4h.nodes.Node.has_feature`::

       >>> doc.has_feature('xpath')
       True


Filtering Node Lists
--------------------

Many *xml4h* node attributes return a list of nodes as a
:class:`~xml4h.nodes.NodeList` object which confers some special filtering
powers.  You get this special node list object from attributes like
``children``, ``ancestors``, and ``siblings``, and from the ``find`` search
method.

Here are some examples of how you can easily filter a
:class:`~xml4h.nodes.NodeList` to get just the
nodes you need:

- Get the first child node using the ``filter`` method::

      >>> # Filter to get just the first child
      >>> doc.root.children.filter(first_only=True)
      <xml4h.nodes.Element: "Film">

      >>> # The document has 7 <Film> element children of the root
      >>> len(doc.root.children)
      7

- Get the first child node by treating ``children`` as a callable::

      >>> doc.root.children(first_only=True)
      <xml4h.nodes.Element: "Film">

  When you treat the node list as a callable it calls the ``filter`` method
  behind the scenes, but since doing it the callable way is quicker and
  clearer in code we will use that approach from now on.

- Get the first child node with the ``child`` filtering method, which accepts
  the same constraints as the ``filter`` method::

      >>> doc.root.child()
      <xml4h.nodes.Element: "Film">

      >>> # Apply filtering with child
      >>> print doc.root.child('WrongName')
      None

- Get the first of a set of children with the ``first`` attribute::

      >>> doc.root.children.first
      <xml4h.nodes.Element: "Film">


- Filter the node list by name::

      >>> for n in doc.root.children('Film'):
      ...     print n.Title.text
      And Now for Something Completely Different
      Monty Python and the Holy Grail
      Monty Python's Life of Brian
      Monty Python Live at the Hollywood Bowl
      Monty Python's The Meaning of Life
      Monty Python: Almost the Truth (The Lawyer's Cut)
      A Liar's Autobiography: Volume IV

      >>> len(doc.root.children('WrongName'))
      0

  .. note::
     Passing a node name as the first argument will match the *local* name of
     a node. You can match the full node name, which might include a prefix
     for example, with a call like: ``.children(local_name='SomeName')``.

- Filter with a custom function::

      >>> # Filter to films released in the year 1979
      >>> for n in doc.root.children('Film',
      ...         filter_fn=lambda node: node.attributes['year'] == '1979'):
      ...     print n.Title.text
      Monty Python's Life of Brian


"Magical" Node Traversal
------------------------

To make it easy to traverse XML documents with a known structure *xml4h*
performs some minor magic when you look up attributes or keys on Document
and Element nodes.  If you like, you can take advantage of magical traversal
to avoid peppering your code with ``find`` and ``xpath`` searches, or with
filter constraints on ``children`` node attributes.

Depending on how you feel about magical behaviour this feature might feel like
a great convenience or a behaviour to regard with deep suspicion. The right
attitude probably lies somewhere in the middle...

Here is an example of retrieving information from our Monty Python films
document using element names as Python attributes (``MontyPythonFilms``,
``Film``, ``Title``) and XML attribute names as Python keys (``year``)::

    >>> for film in doc.MontyPythonFilms.Film:
    ...     print film['year'], ':', film.Title.text  # doctest:+ELLIPSIS
    1971 : And Now for Something Completely Different
    1974 : Monty Python and the Holy Grail
    ...

To minimise the chances of unexpected behaviour from too much (black) magic
there are restrictions on the format of Python attribute names that *xml4h*
use to look up child Elements. The attribute name:

- cannot start with any underscore characters
- must contain at least one uppercase character, or
- if your XML element names are all lowercase (yuck!) you can tell *xml4h* to
  treat it specially by adding a single underscore character to the end of the
  name. For example, to traverse a child element named ``myelement`` you
  would use the Python attribute name ``myelement_``.

There are more gory details in the documentation at
:class:`~xml4h.nodes.NodeAttrAndChildElementLookupsMixin`.

.. note::
   The behaviour of namespaced XML elements and attributes is inconsistent.
   You can do magical traversal of elements regardless of what namespace the
   elements are in, but to look up XML attributes with a namespace prefix
   you must include that prefix in the name e.g. ``prefix:attribute-name``.


Manipulating Nodes
------------------

- Set name and value
- delete



Working with Elements
---------------------



.. _wrap-unwrap-nodes:

Wrapping and Unwrapping *xml4h* Nodes
-------------------------------------

You can easily convert to or from *xml4h*'s wrapped version of an
implementation node. For example, if you prefer the *lxml* library's
`ElementMaker <http://lxml.de/tutorial.html#the-e-factory>`_ document builder
approach to the :ref:`xml4h Builder <builder>`, you can create a document
in *lxml*...

::

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

...and then convert (or, more accurately, wrap) the *lxml* nodes with the
appropriate adapter to make them *xml4h* versions::

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

