===============
Advanced Topics
===============


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

- an "xmlns" attribute on an element assigns a *namespace URI* to that
  element, and also defines the shorthand *prefix* for the namespace::

      <AnElement xmlns:my-prefix="urn:example-uri">

  .. note::
     Technically the "xmlns" attribute must itself also be in the special XML
     namespacing namespace "http://www.w3.org/2000/xmlns/". You needn't care
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
    >>> print root.xml()
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
    >>> elem4.attrs({'my-ns:attr1': 'value'})

    >>> print elem4.xml()
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


.. _xml-lib-adapters:

XML Libarary Adapters
=====================


.. _best-adapter:

"Best" Adapter
--------------


Choose Your Own Adapter
-----------------------


Quirks
------

