=======
Builder
=======

*xml4h* includes a document builder utility that makes it easy to create valid,
guaranteed well-formed XML documents using relatively sparse python code. It
is intended to make it so easy to create XML that you will no longer be
tempted to cobble together documents by concatenating strings, even for
simple cases.

Internally, the builder uses the DOM-building features of an underlying XML
library exposed through an adapter (see :ref:`xml-lib-adapters`). This means
that you can be sure you will generate a valid document.

Here is some example code::

    >>> import xml4h
    >>> xmlb = (xml4h.build('MontyPythonFilms')
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

    >>> xmlb.write_doc(indent=True)  # doctest:+ELLIPSIS
    <?xml version="1.0" encoding="utf-8"?>
    <MontyPythonFilms source="http://en.wikipedia.org/wiki/Monty_Python">
        <Film year="1971">
            <Title>And Now for Something Completely Different</Title>
            <Description>A collection of sketches from the first and second...
        </Film>
        <Film year="1974">
            <Title>Monty Python and the Holy Grail</Title>
            <Description>King Arthur and his knights embark on a low-budget...
        </Film>
    </MontyPythonFilms>


Getting Started
---------------

You typically create a new XML document and builder by calling the
:func:`xml4h.build` function with the name of the root element::

    >>> root_b = xml4h.build('RootElement')

The function returns an :class:`xml4h.builder.Builder` object that represents
the *RootElement* and allows you to manipulate this element's attributes
or to add child elements.

Once you have the first builder instance, every action you perform on a
builder that adds content to the XML document will return an instance of
this same class representing an underlying element.

Builder methods that add content to the current element -- such as attributes,
text, or namespaces -- return the same builder instance representing the
current element::

    >>> root_b = root_b.attributes({'a': 1, 'b': 2}, c=3)

    >>> root_b.dom_element
    <xml4h.nodes.Element: "RootElement">

    >>> root_b.dom_element.attributes
    <xml4h.nodes.AttributeDict: OrderedDict([('a', '1'), ('b', '2'), ('c', '3')])>

.. note::
   As you can see above, the element node represented by a builder instance is
   available through the :meth:`~xml4h.builder.Builder.dom_element` method.

When you add a new child element the result is a builder instance representing
the child element, *not the original element*::

    >>> child1_b = root_b.element('ChildElement1')

    >>> child2_b = root_b.element('ChildElement2')
    >>> child2_b.dom_element
    <xml4h.nodes.Element: "ChildElement2">
    >>> child2_b.dom_element.parent
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

    >>> b = (xml4h.build('RootElement')
    ...         .attributes({'a': 1, 'b': 2}, c=3)
    ...     .element('ChildElement1').up()  # NOTE the up() method
    ...     .element('ChildElement2')
    ...     )

    >>> b.write_doc(indent=4)
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

   It is a good idea to wrap the :func:`~xml4h.build` function call and all
   following chained methods in parentheses, so you don't need to put
   backslash (\\) characters at the end of every line.

The code above introduces a very important builder method:
:meth:`~xml4h.builder.Builder.up`. This method returns a builder instance
representing the current element's parent, or indeed any ancestor.

Without the ``up()`` method every child element a builder created would leave
you deeper in the document structure with no way to return to prior elements
and do things like add sibling nodes or hierarchies.

To help reduce the number of ``up()`` method calls you need to include in
your code, this method can also jump up multiple levels or to a named ancestor
element::

    >>> # A builder that references a deeply-nested element:
    >>> deep_b = (xml4h.build('Root')
    ...     .element('Deep')
    ...         .element('AndDeeper')
    ...             .element('AndDeeperStill')
    ...                 .element('UntilWeGetThere')
    ...     )
    >>> deep_b.dom_element
    <xml4h.nodes.Element: "UntilWeGetThere">

    >>> # Jump up 4 levels, back to the root element
    >>> deep_b.up(4).dom_element
    <xml4h.nodes.Element: "Root">

    >>> # Jump up to a named ancestor element
    >>> deep_b.up('Root').dom_element
    <xml4h.nodes.Element: "Root">

.. note::
   We recommend you use :meth:`~xml4h.builder.Builder.up` calls to return
   back one level for every :meth:`~xml4h.builder.Builder.element` method
   (or alias) when you chain methods to avoid making subtle errors in
   your document's structure.


Shorthand Methods
-----------------

To make your XML-producing code even less verbose and quicker to type, the
builder has shorthand "alias" methods corresponding to the full names.

For example, instead of calling ``element()`` to create a new
child element, you can instead use the equivalent ``elem()`` or ``e()``
methods. Similarly, instead of typing ``attributes()`` you can use ``attrs()``
or ``a()``.

Here are the methods and method aliases for adding content to an XML document:

===================  ==========================  ================
XML Node Created     Builder method              Aliases
===================  ==========================  ================
Element              ``element``                 ``elem``, ``e``
Attribute            ``attributes``              ``attrs``, ``a``
Text                 ``text``                    ``t``
CDATA                ``cdata``                   ``data``, ``d``
Comment              ``comment``                 ``c``
Process Instruction  ``processing_instruction``  ``inst``, ``i``
===================  ==========================  ================

These shorthand method aliases are convenient and lead to even less cruft
around the actual XML content you are interested in. But on the other hand
they are much less explicit than the longer versions, so use them judiciously.


Access the DOM
--------------

The XML builder is merely a layer of convenience methods that sits on the
:mod:`xml4h.nodes` DOM API. This means you can quickly access the underlying
nodes from a builder if you need to inspect them or manipulate them in a
way the builder doesn't allow.

The :attr:`~xml4h.builder.Builder.dom_element` attribute returns a builder's
underlying :class:`~xml4h.nodes.Element`, and the
:attr:`~xml4h.builder.Builder.root` attribute returns the document's
root element.

The :attr:`~xml4h.builder.Builder.document` attribute returns a builder's
underlying :class:`~xml4h.nodes.Document`.

The :mod:`xml4h.nodes` api is described in :ref:`api-nodes`.


Building on an Existing DOM
---------------------------

When you are building an XML document from scratch you will generally use the
the :func:`~xml4h.build` function described in `Getting Started`_. However,
what if you want ot add content to a parsed XML document DOM you have already?

To wrap an :class:`~xml4h.nodes.Element` DOM node with a builder you simply
provide the element node to the same ``builder()`` method used previously and
it will do the right thing.

Here is an example of parsing an existing XML document, locating an element
of interest, constructing a builder from that element, and adding some
content. Luckily, the code is simpler than that description...

::

    >>> # Parse an XML document
    >>> doc = xml4h.parse('tests/data/monty_python_films.xml')

    >>> # Find an Element node of interest
    >>> lob_film_elem = doc.MontyPythonFilms.Film[2]
    >>> lob_film_elem.Title.text
    "Monty Python's Life of Brian"

    >>> # Construct a builder from the element
    >>> lob_builder = xml4h.build(lob_film_elem)

    >>> # Add content
    >>> (lob_builder.attrs(stars=5)
    ...     .elem('Review').t('One of my favourite films!').up()
    ...     ).write(indent=True)  # doctest:+ELLIPSIS
    <Film stars="5" year="1979">
        <Title>Monty Python's Life of Brian</Title>
        <Description>Brian is born on the first Christmas, in the stable...
        <Review>One of my favourite films!</Review>
    </Film>


Hydra-Builder
-------------

Because each builder class instance is independent, an advanced technique for
constructing complex documents is to use multiple builders anchored at
different places in the DOM. In some situations, the ability to add content
to different places in the same document can be very handy.

Here is a trivial example of this technique::

    >>> # Create two Elements in a doc to store even or odd numbers
    >>> odd_b = xml4h.build('EvenAndOdd').elem('Odd')
    >>> even_b = odd_b.up().elem('Even')

    >>> # Populate the numbers from a loop
    >>> for i in range(1, 11):  # doctest:+ELLIPSIS
    ...     if i % 2 == 0:
    ...         even_b.elem('Number').text(i)
    ...     else:
    ...         odd_b.elem('Number').text(i)
    <...

    >>> # Check the final document
    >>> odd_b.write_doc(indent=True)
    <?xml version="1.0" encoding="utf-8"?>
    <EvenAndOdd>
        <Odd>
            <Number>1</Number>
            <Number>3</Number>
            <Number>5</Number>
            <Number>7</Number>
            <Number>9</Number>
        </Odd>
        <Even>
            <Number>2</Number>
            <Number>4</Number>
            <Number>6</Number>
            <Number>8</Number>
            <Number>10</Number>
        </Even>
    </EvenAndOdd>
