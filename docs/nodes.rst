=========
DOM Nodes
=========

*xml4h* provides node objects and convenience methods that make it easier to
work with an in-memory XML document object model (DOM).

This section of the document covers the main features of *xml4h* nodes.
For the full API-level documentation see :ref:`api-nodes`.

.. _node-traversal:

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
- Nodes that have a value expose it via the ``value`` attribute.
- A node's ``parent`` attribute returns its parent, while the ``ancestors``
  attribute returns a list containing its parent, grand-parent,
  great-grand-parent etc.
- A node's ``children`` attribute returns the child nodes that belong to it,
  while the ``siblings`` attribute returns all other nodes that belong to its
  parent. You can also get the ``siblings_before`` or ``siblings_after`` the
  current node.
- Look up a node's namespace URI with ``namespace_uri`` or the alias
  ``ns_uri``.
- Check what type of :class:`~xml4h.nodes.Node` you have with Boolean
  attributes like ``is_element``, ``is_text``, ``is_entity`` etc.


.. _magical-node-traversal:

"Magical" Node Traversal
------------------------

To make it easy to traverse XML documents with a known structure *xml4h*
performs some minor magic when you look up attributes or keys on Document
and Element nodes.  If you like, you can take advantage of magical traversal
to avoid peppering your code with ``find`` and ``xpath`` searches, or with
``child`` and ``children`` node attribute lookups.

The principle is simple:

- Child elements are available as Python attributes of the parent element
  class.
- XML element attributes are available as a Python dict in the owning element.

Here is an example of retrieving information from our Monty Python films
document using element names as Python attributes (``MontyPythonFilms``,
``Film``, ``Title``) and XML attribute names as Python keys (``year``)::

    >>> # Parse an example XML document about Monty Python films
    >>> import xml4h
    >>> doc = xml4h.parse('tests/data/monty_python_films.xml')

    >>> for film in doc.MontyPythonFilms.Film:
    ...     print(film['year'] + ' : ' + film.Title.text)  # doctest:+ELLIPSIS
    1971 : And Now for Something Completely Different
    1974 : Monty Python and the Holy Grail
    ...

Python class attribute lookups of child elements work very well when your XML
document contains only camel-case tag names ``LikeThisOne`` or ``LikeThat``.
However, if your document contains lower-case tag names there is a chance the
element names will clash with existing Python attribute or method names in the
*xml4h* classes.

To work around this potential issue you can add an underscore (``_``)
character at the end of a magical attribute lookup to avoid the naming clash;
*xml4h* will remove that character before looking for a child element. For
example, to look up a child of the element ``elem1`` which is named ``child``,
the code ``elem1.child_`` will return the child element whereas ``elem1.child``
would access the :meth:`~xml4h.nodes.Node.child` Node method instead.

.. note::
   Not all XML child element tag names are accessible using magical traversal.
   Names with leading underscore characters will not work, and nor will names
   containing hyphens because they are not valid Python attribute names. If you
   have to deal with XML names like this use the full API methods like
   :meth:`~xml4h.nodes.Node.child` and :meth:`~xml4h.nodes.Node.children`
   instead.

All the gory details about how magical traversal works are documented at
:class:`~xml4h.nodes.NodeAttrAndChildElementLookupsMixin`.  Depending on how
you feel about magical behaviour this feature might feel like a great
convenience, or black magic that makes you wary. The right attitude probably
lies somewhere in the middle...

.. warning::
   The behaviour of namespaced XML elements and attributes is inconsistent.
   You can do magical traversal of elements regardless of what namespace the
   elements are in, but to look up XML attributes with a namespace prefix
   you must include that prefix in the name e.g. ``prefix:attribute-name``.


Searching with Find and XPath
-----------------------------

There are two ways to search for elements within an *xml4h* document: ``find``
and ``xpath``.

The find methods provided by the library are easy to use but can only perform
relatively simple searches that return :class:`~xml4h.nodes.Element` results,
whereas you need to be familiar with XPath query syntax to search effectively
with the ``xpath`` method but you can perform more complex searches and get
results other than just elements.

Find Methods
............

*xml4h* provides three different find methods:

- :meth:`~xml4h.nodes.Node.find` searches descendants of the current node for
  elements matching the given constraints. You can search by element name,
  by namespace URI, or with no constraints at all::

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
      >>> print(doc.find_first('OopsWrongName'))
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

:meth:`~xml4h.nodes.XPathMixin.xpath` takes an XPath query string and returns
the result which may be a list of elements, a list of attributes, a list of
values, or a single value. The result depends entirely on the kind of query you
perform.

.. note::
   XPath querying is currently only available if you use the *lxml* or
   *ElementTree* implementation libraries. You can check whether the XPath
   feature is available with :meth:`~xml4h.nodes.Node.has_feature`.

.. note::
   Although *ElementTree* supports XPath queries, this support is
   `very limited <http://effbot.org/zone/element-xpath.htm>`_ and most of the
   example XPath queries below **will not work**. If you want to use XPath, you
   should install *lxml* for better support.

XPath queries are powerful and complex so we cannot describe them in detail
here, but we can at least present some useful examples. Here are queries that
perform the same work as the find queries we saw above::

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

You can also do things with XPath queries that you simply cannot with the
*find* method, such as find all the attributes of a certain name or apply
rich constraints to the query::

      >>> # Query for all year attributes
      >>> doc.xpath('//@year')
      ['1971', '1974', '1979', '1982', '1983', '2009', '2012']

      >>> # Query for the title of the film released in 1982
      >>> doc.xpath('//Film[@year="1982"]/Title/text()')
      ['Monty Python Live at the Hollywood Bowl']


Namespaces and XPath
....................

Finally, let's discuss how you can run XPath queries on documents with
namespaces, because unfortunately this is not a simple subject.

First, you need to understand that if you are working with a namespaced
document your XPath queries must refer to those namespaces or they will not
find anything::

    >>> # Parse a namespaced version of the Monty Python Films doc
    >>> ns_doc = xml4h.parse('tests/data/monty_python_films.ns.xml')
    >>> print(ns_doc.xml())  #doctest:+ELLIPSIS
    <?xml version="1.0" encoding="utf-8"?>
    <MontyPythonFilms source="http://en.wikipedia.org/wiki/Monty_Python" xmlns="uri:monty-python" xmlns:work="uri:artistic-work">
        <work:Film year="1971">
            <Title>And Now for Something Completely Different</Title>
            ...

    >>> # XPath queries without prefixes won't find namespaced elements
    >>> ns_doc.xpath('//Film')
    []

To refer to namespaced nodes in your query the namespace must have a prefix
alias assigned to it. You can specify prefixes when you call the *xpath* method
by providing a ``namespaces`` keyword argument with a dictionary of
alias-to-URI mappings::

    >>> # Specify explicit prefix alias mappings
    >>> films = ns_doc.xpath('//x:Film', namespaces={'x': 'uri:artistic-work'})
    >>> len(films)
    7

Or, preferably, if your document node already has prefix mappings you can use
them directly::

    >>> # Our root node already has a 'work' prefix defined...
    >>> ns_doc.root['xmlns:work']
    'uri:artistic-work'

    >>> # ...so we can use this prefix directly
    >>> films = ns_doc.root.xpath('//work:Film')
    >>> len(films)
    7

Another gotcha is when a document has a default namespace. The default
namespace applies to every descendent node without its own namespace, but XPath
doesn't have a good way of dealing with this since there is no such thing as
a "default namespace" prefix alias.

*xml4h* helps out by providing just such an alias: the underscore (``_``)::

    >>> # Our document root has a default namespace
    >>> ns_doc.root.ns_uri
    'uri:monty-python'

    >>> # You need a prefix alias that refers to the default namespace
    >>> ns_doc.xpath('//Title')
    []

    >>> # You could specify it explicitly...
    >>> titles = ns_doc.xpath('//x:Title',
    ...                       namespaces={'x': ns_doc.root.ns_uri})
    >>> len(titles)
    7

    >>> # ...or use xml4h's special default namespace prefix: _
    >>> titles = ns_doc.xpath('//_:Title')
    >>> len(titles)
    7


Filtering Node Lists
--------------------

Many *xml4h* node attributes return a list of nodes as a
:class:`~xml4h.nodes.NodeList` object which confers some special filtering
powers.  You get this special node list object from attributes like
``children``, ``ancestors``, and ``siblings``, and from the ``find`` search
method if it has element results.

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
      >>> print(doc.root.child('WrongName'))
      None

- Get the first of a set of children with the ``first`` attribute::

      >>> doc.root.children.first
      <xml4h.nodes.Element: "Film">


- Filter the node list by name::

      >>> for n in doc.root.children('Film'):
      ...     print(n.Title.text)
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
     for example, with a call like: ``.children(name='SomeName')``.

- Filter with a custom function::

      >>> # Filter to films released in the year 1979
      >>> for n in doc.root.children('Film',
      ...         filter_fn=lambda node: node.attributes['year'] == '1979'):
      ...     print(n.Title.text)
      Monty Python's Life of Brian


Manipulating Nodes and Elements
-------------------------------

*xml4h* provides simple methods to manipulate the structure and content of an
XML DOM. The methods available depend on the kind of node you are interacting
with, and by far the majority are for working with
:class:`~xml4h.nodes.Element` nodes.


Delete a Node
.............

Any node can be removes from its owner document with
:meth:`~xml4h.nodes.Node.delete`::

    >>> # Before deleting a Film element there are 7 films
    >>> len(doc.MontyPythonFilms.Film)
    7

    >>> doc.MontyPythonFilms.children('Film')[-1].delete()
    >>> len(doc.MontyPythonFilms.Film)
    6

.. note::
   By default deleting a node also destroys it, but it can optionally be left
   intact after removal from the document by including the ``destroy=False``
   option.

Name and Value Attributes
.........................

Many nodes have low-level name and value properties that can be read from and
written to.  Nodes with names and values include Text, CDATA, Comment,
ProcessingInstruction, Attribute, and Element nodes.

Here is an example of accessing the low-level name and value properties of a
Text node::

    >>> text_node = doc.MontyPythonFilms.child('Film').child('Title').child()
    >>> text_node.is_text
    True

    >>> text_node.name
    '#text'
    >>> text_node.value
    'And Now for Something Completely Different'

And here is the same for an Attribute node::

    >>> # Access the name/value properties of an Attribute node
    >>> year_attr = doc.MontyPythonFilms.child('Film').attribute_node('year')
    >>> year_attr.is_attribute
    True

    >>> year_attr.name
    'year'
    >>> year_attr.value
    '1971'

The name attribute of a node is not necessarily a plain string, in the case of
nodes within a defined namespaced the ``name`` attribute may comprise two
components: a ``prefix`` that represents the namespace, and a ``local_name``
which is the plain name of the node ignoring the namespace. For more
information on namespaces see :ref:`xml4h-namespaces`.

Import a Node and its Descendants
.................................

In addition to manipulating nodes in a single XML document directly, you can
also import a node (and all its descendant) from another document using a node
clone or transplant operation.

There are two ways to import a node and its descendants:

- Use the :meth:`~xml4h.nodes.Node.clone_node` Node method or
  :meth:`~xml4h.builder.Builder.clone` Builder method to copy a node into your
  document without removing it from its original document.
- Use the :meth:`~xml4h.nodes.Node.transplant_node` Node method or
  :meth:`~xml4h.builder.Builder.transplant` Builder method to transplant a node
  into your document and remove it from its original document.

Here is an example of transplanting a node into a document (which also happens
to undo the damage we did to our example DOM in the ``delete()`` example
above)::

    >>> # Build a new document containing a Film element
    >>> film_builder = (xml4h.build('DeletedFilm')
    ...     .element('Film').attrs(year='1971')
    ...         .element('Title')
    ...             .text('And Now for Something Completely Different').up()
    ...         .element('Description').text(
    ...             "A collection of sketches from the first and second TV"
    ...             " series of Monty Python's Flying Circus purposely"
    ...             " re-enacted and shot for film.")
    ...     )

    >>> # Transplant the Film element from the new document
    >>> node_to_transplant = film_builder.root.child('Film')
    >>> doc.MontyPythonFilms.transplant_node(node_to_transplant)
    >>> len(doc.MontyPythonFilms.Film)
    7

When you transplant a node from another document it is removed from that
document::

    >>> # After transplanting the Film node it is no longer in the original doc
    >>> len(film_builder.root.find('Film'))
    0

If you need to leave the original document unchanged when importing a node use
the clone methods instead.

Working with Elements
.....................

Element nodes have the most methods to access and manipulate their content,
which is fitting since this is the most useful type of node and you will deal
with elements regularly.

The leaf elements in XML documents often have one or more
:class:`~xml4h.nodes.Text` node children that contain the element's data
content. While you could iterate over such text nodes as child nodes, *xml4h*
provides the more convenient text accessors you would expect::

    >>> title_elem = doc.MontyPythonFilms.Film[0].Title
    >>> orig_title = title_elem.text
    >>> orig_title
    'And Now for Something Completely Different'

    >>> title_elem.text = 'A new, and wrong, title'
    >>> title_elem.text
    'A new, and wrong, title'

    >>> # Let's put it back the way it was...
    >>> title_elem.text = orig_title

Elements also have attributes that can be manipulated in a number of ways.

Look up an element's attributes with:

- the :meth:`~xml4h.nodes.Element.attributes` attribute (or aliases ``attrib``
  and ``attrs``) that return an ordered dictionary of attribute names and
  values::

      >>> film_elem = doc.MontyPythonFilms.Film[0]
      >>> film_elem.attributes
      <xml4h.nodes.AttributeDict: [('year', '1971')]>

- or by obtaining an element's attributes as :class:`~xml4h.nodes.Attribute`
  nodes, though that is only likely to be useful in unusual circumstances::

      >>> film_elem.attribute_nodes
      [<xml4h.nodes.Attribute: "year">]

      >>> # Get a specific attribute node by name or namespace URI
      >>> film_elem.attribute_node('year')
      <xml4h.nodes.Attribute: "year">

- and there's also the "magical" keyword lookup technique discussed in
  :ref:`magical-node-traversal` for quickly grabbing attribute values.

Set attribute values with:

- the :meth:`~xml4h.nodes.Element.set_attributes` method, which allows you to
  add attributes without replacing existing ones. This method also supports
  defining XML attributes as a dictionary, list of name/value pairs, or
  keyword arguments::

      >>> # Set/add attributes as a dictionary
      >>> film_elem.set_attributes({'a1': 'v1'})

      >>> # Set/add attributes as a list of name/value pairs
      >>> film_elem.set_attributes([('a2', 'v2')])

      >>> # Set/add attributes as keyword arguments
      >>> film_elem.set_attributes(a3='v3', a4=4)

      >>> film_elem.attributes
      <xml4h.nodes.AttributeDict: [('a1', 'v1'), ('a2', 'v2'), ('a3', 'v3'), ('a4', '4'), ('year', '1971')]>

- the setter version of the :attr:`~xml4h.nodes.Element.attributes` attribute,
  which replaces any existing attributes with the new set::

      >>> film_elem.attributes = {'year': '1971', 'note': 'funny'}
      >>> film_elem.attributes
      <xml4h.nodes.AttributeDict: [('note', 'funny'), ('year', '1971')]>

Delete attributes from an element by:

- using Python's delete-in-dict technique::

      >>> del(film_elem.attributes['note'])
      >>> film_elem.attributes
      <xml4h.nodes.AttributeDict: [('year', '1971')]>

- or by calling the ``delete()`` method on an :class:`~xml4h.nodes.Attribute`
  node.

Finally, the :class:`~xml4h.nodes.Element` class provides a number of methods
for programmatically adding child nodes, for cases where you would rather work
directly with nodes instead of using a :ref:`builder`.

The most complex of these methods is :meth:`~xml4h.nodes.Element.add_element`
which allows you to add a named child element, and to optionally to set the new
element's namespace, text content, and attributes all at the same time. Let's
try an example::

    >>> # Add a Film element with an attribute
    >>> new_film_elem = doc.MontyPythonFilms.add_element(
    ...     'Film', attributes={'year': 'never'})

    >>> # Add a Description element with text content
    >>> desc_elem = new_film_elem.add_element(
    ...     'Description', text='Just testing...')

    >>> # Add a Title element with text *before* the description element
    >>> title_elem = desc_elem.add_element(
    ...     'Title', text='The Film that Never Was', before_this_element=True)

    >>> print(doc.MontyPythonFilms.Film[-1].xml())
    <Film year="never">
        <Title>The Film that Never Was</Title>
        <Description>Just testing...</Description>
    </Film>

There are similar methods for handling simpler cases like adding text nodes,
comments etc. Here is an example of adding text nodes::

    >>> # Add a text node
    >>> title_elem = doc.MontyPythonFilms.Film[-1].Title
    >>> title_elem.add_text(', and Never Will Be')

    >>> title_elem.text
    'The Film that Never Was, and Never Will Be'

Refer to the :class:`~xml4h.nodes.Element` documentation for more information
about the other methods for adding nodes.


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

