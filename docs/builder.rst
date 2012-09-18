================
Document Builder
================

xml4h includes a document builder utility that makes it easy to create valid,
guaranteed well-formed XML documents using relatively sparse python code. It
is intended to make it so easy to create XML that you will no longer be
tempted to cobble together documents by concatenating strings, even for
simple cases.

Internally, the builder uses the DOM-building features of an underlying XML
library exposed through an adapter, see :ref:`xml-lib-adapters`. This means
that you can be sure you will generate a valid document.

Here is some example code::

    >>> import xml4h
    >>> xmlb = (xml4h.builder('MontyPythonFilms')
    ...     .attributes({'source': 'http://en.wikipedia.org/wiki/Monty_Python'})
    ...     .element('Film')
    ...         .attributes({'year': 1971})
    ...         .element('Title')
    ...             .text('And Now for Something Completely Different')
    ...             .up()
    ...         .elem('Description').t(
    ...             "A collection of sketches from the first and second TV"
    ...             " series of Monty Python's Flying Circus purposely"
    ...             " re-enacted and shot for film.")
    ...             .up()
    ...         .up()
    ...     .elem('Film')
    ...         .attrs(year=1974)
    ...         .e('Title')
    ...             .t('Monty Python and the Holy Grail')
    ...             .up()
    ...         .e('Description').t(
    ...             "King Arthur and his knights embark on a low-budget search"
    ...             " for the Holy Grail, encountering humorous obstacles along"
    ...             " the way. Some of these turned into standalone sketches."
    ...             ).up()
    ...     )

That produces the XML document::

    >>> xmlb.doc_write(indent=True)
    <?xml version="1.0" encoding="utf-8"?>
    <MontyPythonFilms source="http://en.wikipedia.org/wiki/Monty_Python">
     <Film year="1971">
      <Title>And Now for Something Completely Different</Title>
      <Description>A collection of sketches from the first and second TV series of Monty Python's Flying Circus purposely re-enacted and shot for film.</Description>
     </Film>
     <Film year="1974">
      <Title>Monty Python and the Holy Grail</Title>
      <Description>King Arthur and his knights embark on a low-budget search for the Holy Grail, encountering humorous obstacles along the way. Some of these turned into standalone sketches.</Description>
     </Film>
    </MontyPythonFilms>

Getting Started
---------------

You create a new XML document and builder by calling the ``xml4h.builder``
method with the name of the root element::

    >>> root_b = xml4h.builder('RootElement')

The method returns an ``xml4h.builder.Builder`` object that represents the
*RootElement* element and allows you to manipulate this element's attributes
or to add child elements.

Once you have the first builder instance, every action you perform on a
builder that adds content to the XML document will return an instance of
this same class representing an underlying element.

Builder methods that add content to the current element -- such as attributes,
text, or namespaces -- return the same builder instance representing the
current element::

    >>> root_b = root_b.attributes({'a': 1, 'b': 2}, c=3)

    >>> root_b.doc_element
    <xml4h.nodes.Element: "RootElement">

    >>> root_b.doc_element.attributes
    <xml4h.nodes.AttributeDict: OrderedDict([('a', '1'), ('b', '2'), ('c', '3')])>

.. note::
   As you can see above, the element node represented by a builder instance is
   available through the ``doc_element`` method.

When you add a new child element the result is a builder instance representing
the child element, *not the original element*::

    >>> child1_b = root_b.element('ChildElement1')

    >>> child2_b = root_b.element('ChildElement2')
    >>> child2_b.doc_element
    <xml4h.nodes.Element: "ChildElement2">
    >>> child2_b.doc_element.parent
    <xml4h.nodes.Element: "RootElement">

This feature of the builder can be a little confusing, but it allows for the
very convenient method-chaining feature that gives the builder its power.

.. _builder-method-chaining:

Method Chaining
---------------

Because every builder method that adds content to the XML document returns
a builder instance representing the nearest (or newest) element, you can
chain together many method calls to construct your document without any
need for intermediate variables.

For example, the example code in the previous section used the variables
``root_b``, ``child1_b`` and ``child2_b`` to store builder instances but
this is not necessary. Here is the method-chaining approach to accomplish
the same thing::

    >>> b = (xml4h.builder('RootElement')
    ...         .attributes({'a': 1, 'b': 2}, c=3)
    ...     .element('ChildElement1').up()  # NOTE the up() method
    ...     .element('ChildElement2')
    ...     )

    >>> b.doc_write(indent=4)
    <?xml version="1.0" encoding="utf-8"?>
    <RootElement a="1" b="2" c="3">
        <ChildElement1/>
        <ChildElement2/>
    </RootElement>

Notice how you can use chained method calls to write code with a structure
that mirrors that of the XML document you want to produce? This makes it
much easier to spot errors in your code than it would be if you were to
concatenate strings.

.. note::

   It is a good idea to wrap the ``xml4h.builder`` method call and all
   following chained methods in parentheses, so you don't need to put
   backslash (\) characters at the end of every line.

The code above introduces a very important builder method: ``up()``. This
method returns a builder instance representing the current element's parent,
or indeed any ancestor.

Without the ``up()`` method every child element a builder created would leave
you deeper in the document structure with no way to return to prior elements
and do things like add sibling nodes or hierarchies.

To help reduce the number of ``up()`` method calls you need to include in
your code, this method can also jump up multiple levels or to a named ancestor
element::

    >>> # A builder that references a deeply-nested element:
    >>> deep_b = (xml4h.builder('Root')
    ...     .element('Deep1')
    ...         .element('AndDeeper')
    ...             .element('AndDeeperStill')
    ...                 .element('UntilWeGetThere')
    ...     )
    >>> deep_b.doc_element
    <xml4h.nodes.Element: "UntilWeGetThere">

    >>> # Jump up 4 levels, back to the root element
    >>> deep_b.up(4).doc_element
    <xml4h.nodes.Element: "Root">

    >>> # Jump up to a named ancestor element
    >>> deep_b.up('Root').doc_element
    <xml4h.nodes.Element: "Root">

.. note::
   Best practice when chaining builder method calls is to use ``up()`` calls
   to return back one level for every ``element()`` (or equivalent) method.
   Do this to avoid making subtle errors in your document's structure.


Shorthand Methods
-----------------

Access or Write the DOM
-----------------------

Traversing Elements
-------------------

Hydra-Builder
-------------


