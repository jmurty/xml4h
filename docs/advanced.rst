========
Advanced
========


.. _xml4h-namespaces:

Namespaces
==========

*xml4h* supports using XML namespaces in a number of ways, and tries to make
this sometimes complex and fiddly aspect of XML a little easier to deal with.

Namespace URIs
--------------

XML document nodes can be associated with a *namespace URI* which uniquely
identifies the namespace.  At bottom a URI is really just a name to identifiy
the namespace, which may or may not point at an actual resource.

Namespace URIs are the core piece of the namespacing puzzle, everything else is
extras.

Namespace URI values are assigned to a node in one of three ways:

- an ``xmlns`` attribute on an element assigns a *namespace URI* to that
  element, and may also define a shorthand *prefix* for the namespace::

      <AnElement xmlns:my-prefix="urn:example-uri">

  .. note::
     Technically the ``xmlns`` attribute must itself also be in the special XML
     namespacing namespace http://www.w3.org/2000/xmlns/. You needn't care
     about this.

- a tag or attribute name includes a *prefix* alias portion that specifies the
  namespace the item belongs to::

      <my-prefix:AnotherElement attr1="x" my-prefix:attr2="i am namespaced">

  A prefix alias can be defined using an "xmlns" attribute as described above,
  or by using the Builder :meth:`~xml4h.Builder.ns_prefix` or Node
  :meth:`~xml4h.nodes.Node.set_ns_prefix` methods.

- in an apparent effort to reduce confusion around namespace URIs and prefixes,
  some XML libraries avoid prefix aliases altogether and instead require you to
  specify the full *namespace URI* as a prefix to tag and attribute names
  using a special syntax with braces::

      >>> tagname = '{urn:example-uri}YetAnotherWayToNamespace'

  .. note::
     In the author's opinion, using a non-standard way to define namespaces
     does not reduce confusion. *xml4h* supports this approach technically but
     not philosphically.

*xml4h* allows you to assign namespace URIs to document nodes when using the
Builder::

    >>> # Assign a default namespace with ns_uri
    >>> import xml4h
    >>> b = xml4h.build('Doc', ns_uri='ns-uri')
    >>> root = b.root

    >>> # Descendent without a namespace inherit their ancestor's default one
    >>> elem1 = b.elem('Elem1').dom_element
    >>> elem1.namespace_uri
    'ns-uri'

    >>> # Define a prefix alias to assign a new or existing namespace URI
    >>> elem2 = b.ns_prefix('my-ns', 'second-ns-uri') \
    ...     .elem('my-ns:Elem2').dom_element
    >>> print(root.xml())
    <Doc xmlns="ns-uri" xmlns:my-ns="second-ns-uri">
        <Elem1/>
        <my-ns:Elem2/>
    </Doc>

    >>> # Or use the explicit URI prefix approach, if you must
    >>> elem3 = b.elem('{third-ns-uri}Elem3').dom_element
    >>> elem3.namespace_uri
    'third-ns-uri'

And when adding nodes with the API::

    >>> # Define the ns_uri argument when creating a new element
    >>> elem4 = root.add_element('Elem4', ns_uri='fourth-ns-uri')

    >>> # Attributes can be namespaced too
    >>> elem4.set_attributes({'my-ns:attr1': 'value'})

    >>> print(elem4.xml())
    <Elem4 my-ns:attr1="value" xmlns="fourth-ns-uri"/>


Filtering by Namespace
----------------------

*xml4h* allows you to find and filter nodes based on their namespace.

The :meth:`~xml4h.nodes.Node.find` method takes a ``ns_uri`` keyword argument to
return only elements in that namespace::

    >>> # By default, find ignores namespaces...
    >>> [n.local_name for n in root.find()]
    ['Elem1', 'Elem2', 'Elem3', 'Elem4']
    >>> # ...but will filter by namespace URI if you wish
    >>> [n.local_name for n in root.find(ns_uri='fourth-ns-uri')]
    ['Elem4']

Similarly, a node's children listing can be filtered::

    >>> len(root.children)
    4
    >>> root.children(ns_uri='ns-uri')
    [<xml4h.nodes.Element: "Elem1">]

XPath queries can also filter by namespace, but the
:meth:`~xml4h.nodes.Node.xpath` method needs to be given a dictionary mapping
of prefix aliases to URIs::

    >>> root.xpath('//ns4:*', namespaces={'ns4': 'fourth-ns-uri'})
    [<xml4h.nodes.Element: "Elem4">]

.. note::
   Normally, because XPath queries rely on namespace prefix aliases, they
   cannot find namespaced nodes in the default namespace which has an "empty"
   prefix name. *xml4h* works around this limitation by providing the special
   empty/default prefix alias '_'.


Element Names: Local and Prefix Components
------------------------------------------

When you use a namespace prefix alias to define the namespace an element or
attribute belongs to, the name of that node will be made up of two components:

- *prefix* - the namespace alias.
- *local* - the real name of the node, without the namespace alias.

*xml4h* makes the full (qualified) name, and the two components, available at
node attributes::

    >>> # Elem2's namespace was defined earlier using a prefix alias
    >>> elem2
    <xml4h.nodes.Element: "my-ns:Elem2">

    # The full node name...
    >>> elem2.name
    'my-ns:Elem2'
    >>> # ...comprises a prefix...
    >>> elem2.prefix
    'my-ns'
    >>> # ...and a local name component
    >>> elem2.local_name
    'Elem2'

    >>> # Here is an element without a prefix alias
    >>> elem1.name
    'Elem1'
    >>> elem1.prefix == None
    True
    >>> elem1.local_name
    'Elem1'


.. _xml-lib-architecture:

*xml4h* Architecture
====================

To best understand the *xml4h* library and to use it appropriately in demanding
situations, you should appreciate what the library is not.

*xml4h* is not a full-fledged XML library in its own right, far from it.
Instead of implementing low-level document parsing and manipulation tools, it
operates as an abstraction layer on top of the pre-existing XML processing
libraries you already know.

This means the improved API and tool suite provided by *xml4h* work by
mediating operations you perform, asking the underlying XML library to do the
work, and packaging up the results of this work as wrapped *xml4h* objects.

This approach has a number of implications, good and bad.

On the good side:

- you can start using and benefiting from *xml4h* in an existing projects that
  already use a supported XML library without any impact, it can fit right in.
- *xml4h* can take advantage of the existing powerful and fast XML libraries to
  do its work.
- by providing an abstraction layer over multiple libraries, *xml4h* can make
  it (relatively) easy to switch the underlying library without you needing to
  rewrite your own XML handling code.
- by building on the shoulders of giants, *xml4h* itself can remain relatively
  lightweight and focussed on simplicity and usability.
- the author of *xml4h* does not have to write XML-handling code in C...

On the bad side:

- if the underlying XML libraries available in the Python environment do not
  support a feature (like XPath querying) then that feature will not be
  available in *xml4h*.
- *xml4h* cannot provide radical new XML processing features, since the bulk of
  its work must be done by the underlying library.
- the abstraction layer *xml4h* uses to do its work requires more resources
  than it would to use the underlying library directly, so if you absolutely
  need maximal speed or minimal memory use the library might prove too
  expensive.
- *xml4h* sometimes needs to jump through some hoops to maintain the shared
  abstraction interface over multiple libraries, which means extra work is
  done in Python instead of by the underlying library code in C.

The author believes the benefits of using *xml4h* outweighs the drawbacks in
the majority of real-world situations, or he wouldn't have created the library
in the first place, but ultimately it is up to you to decide where you should
or should not use it.


.. _xml-lib-adapters:

Library Adapters
----------------

To provide an abstraction layer over multiple underlying XML libraries, *xml4h*
uses an "adapter" mechanism to mediate operations on documents. There is an
adapter implementation for each library *xml4h* can work with, each of which
extends the :class:`~xml4h.impls.interface.XmlImplAdapter` class. This base
class includes some standard behaviour, and defines the interface for adapter
implementations (to the extent you can define such interfaces in Python).

The current version of *xml4h* includes adapter implementations for the three
main XML processing libraries for Python:

- :class:`~xml4h.impls.lxml_etree.LXMLAdapter` works with the excellent
  `lxml <http://lxml.de>`_ library which is very full-featured and fast, but
  which is not included in the standard library.
- :class:`~xml4h.impls.xml_etree_elementtree.cElementTreeAdapter` and
  :class:`~xml4h.impls.xml_etree_elementtree.ElementTreeAdapter` work with the
  *ElementTree* libraries included with the standard library of Python versions
  2.7 and later. *ElementTree* is fast and includes support for some basic
  XPath expressions. If the C-based version of ElementTree is available, the
  former adapter is made available and should be used for best performance.
- :class:`~xml4h.impls.xml_dom_minidom.XmlDomImplAdapter` works with the
  `minidom <http://docs.python.org/2/library/xml.dom.minidom.html>`_ W3C-style
  XML library included with the standard library. This library is always
  available but is slower and has fewer features than alternative libraries
  (e.g. no support for XPath)

The adapter layer allows the rest of the *xml4h* library code to remain almost
entirely oblivious to the underlying XML library that happens to be available
at the time. The *xml4h* Builder, Node objects, writer etc. call adapter
methods to perform document operations, and the adapter is responsible for
doing the necessary work with the underlying library.


.. _best-adapter:

"Best" Adapter
--------------

While *xml4h* can work with multiple underlying XML libraries, some of these
libraries are better (faster, more fully-featured) than others so it would be
smart to use the best of the libraries available.

*xml4h* does exactly that: unless you explicitly choose an adapter (see below)
*xml4h* will find the supported libraries in the Python environment and choose
the "best" adapter for you in the circumstances.

Here is the list of libraries *xml4h* will choose from, best to least-best:

- *lxml*
- *(c)ElementTree*
- *ElementTree*
- *minidom*

The :attr:`xml4h.best_adapter` attribute stores the adapter class that *xml4h*
considers to be the best.

.. note:
   You cannot always rely on *xml4h* to choose the right underlying XML library
   for your needs. For cases where you need to use a specific library, such as
   when you have a pre-parsed document object, see `wrap-unwrap-nodes`_.


Choose Your Own Adapter
-----------------------

By default, *xml4h* will choose an adapter and underlying XML library
implementation that it considers the best available. However, in some cases you
may need to have full control over which underlying implementation *xml4h*
uses, perhaps because you will use features of the underlying XML
implementation later on, or because you need the performance characteristics
only available in a particular library.

For these situations it is possible to tell *xml4h* which adapter
implementation, and therefore which underlying XML library, it should use.

To use a specific adapter implementation when parsing a document, or when
creating a new document using the builder, simply provide the optional
``adapter`` keyword argument to the relevant method:

- Parsing::

    >>> # Explicitly use the minidom adapter to parse a document
    >>> minidom_doc = xml4h.parse('tests/data/monty_python_films.xml',
    ...                           adapter=xml4h.XmlDomImplAdapter)
    >>> minidom_doc.root.impl_node  #doctest:+ELLIPSIS
    <DOM Element: MontyPythonFilms at ...

- Building::

    >>> # Explicitly use the lxml adapter to build a document
    >>> lxml_b = xml4h.build('MyDoc', adapter=xml4h.LXMLAdapter)
    >>> lxml_b.root.impl_node  #doctest:+ELLIPSIS
    <Element {http://www.w3.org/2000/xmlns/}MyDoc at ...

- Manipulating::

    >>> # Use xml4h with a cElementTree document object
    >>> import xml.etree.ElementTree as ET
    >>> et_doc = ET.parse('tests/data/monty_python_films.xml')
    >>> et_doc  #doctest:+ELLIPSIS
    <xml.etree.ElementTree.ElementTree object ...
    >>> doc = xml4h.cElementTreeAdapter.wrap_document(et_doc)
    >>> doc.root
    <xml4h.nodes.Element: "MontyPythonFilms">


Check Feature Support
.....................

Because not all underlying XML libraries support all the features exposed by
*xml4h*, the library includes a simple mechanism to check whether a given
feature is available in the current Python environment or with the current
adapter.

To check for feature support call the :meth:`~xml4h.nodes.Node.has_feature`
method on a document node, or
:meth:`~xml4h.impl.interface.XmlImplAdapter.has_feature` on an adapter class.

List of features that are not available in all adapters:

- ``xpath`` - Can perform XPath queries using the
  :meth:`~xml4h.nodes.Node.xpath` method.
- More to come later, probably...

For example, here is how you would test for XPath support in the *minidom*
adapter, which doesn't include it::

    >>> minidom_doc.root.has_feature('xpath')
    False

If you forget to check for a feature and use it anyway, you will get
a :class:`~xml4h.exceptions.FeatureUnavailableException`::

    >>> try:
    ...     minidom_doc.root.xpath('//*')
    ... except Exception as e:
    ...     e  #doctest:+ELLIPSIS
    FeatureUnavailableException('xpath'...


Adapter & Implementation Quirks
-------------------------------

Although *xml4h* aims to provide a seamless abstraction over underlying XML
library implementations this isn't always possible, or is only possible by
performing lots of extra work that affects performance. This section describes
some implementation-specific quirks or differences you may encounter.

.. note:
   This set of quirks is almost certainly incomplete, please report issues you
   find so they can either be fixed (in the best case) or captured here as
   known trouble-spots.

LXMLAdapter - *lxml*
....................

- *lxml* does not have full support for CDATA nodes, which devolve into plain
  text node values when written (by *xml4h* or by *lxml*'s writer).
- Namespaces defined by adding ``xmlns`` element attributes are not properly
  represented in the underlying implementation due to the *lxml* library's
  immutable ``nsmap`` namespace map. Such namespaces are written correcly
  by the *xml4h* writer, but to avoid quirks it is best to specify namespace
  when creating nodes by setting the ``ns_uri`` keyword attribute.
- When *xml4h* writes *lxml*-based documents with namespaces, some node tag
  names may have unnecessary namespace prefix aliases.

(c)ElementTreeAdapter - *ElementTree*
.....................................

- Only the versions of (c)ElementTree included with Python version 2.7 and
  later are supported.
- *ElementTree* supports only a very limited subset of XPath for querying, so
  although the ``has_feature('xpath')`` check returns ``True`` don't expect to
  get the full power of XPath when you use this adapter.
- *ElementTree* does not have full support for CDATA nodes, which devolve into
  plain text node values when written (by *xml4h* or by *ElementTree*'s writer).
- Because *ElementTree* doesn't retain information about a node's parent,
  *xml4h* needs to build and maintain its own records of which nodes are
  parents of which children. This extra overhead might harm performance or
  memory usage.
- *ElementTree* doesn't normally remember explicit namespace definition
  directives when parsing a document. *xml4h* works around this when it is
  asked to parse XML data, but if you parse data outside of *xml4h* then use
  the library on the resultant document the namespace definitions will get
  messed up.

XmlImplAdapter - *minidom*
..........................

- No support for performing XPath queries.
- Slower than alternative C-based implementations.
