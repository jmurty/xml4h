.. _builder:

=======
Builder
=======

*xml4h* includes a document builder tool that makes it easy to create valid,
well-formed XML documents using relatively sparse python code. It makes it so
easy to create XML that you will no longer be tempted to cobble together
documents with error-prone methods like manual string concatenation or a
templating library.

Internally, the builder uses the DOM-building features of an underlying XML
library which means it is (almost) impossible to construct an invalid document.

Here is some example code to build a document about Monty Python films::

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

The code above produces the following XML document (abbreviated)::

    >>> print(xmlb.xml_doc(indent=True))  # doctest:+ELLIPSIS
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
    <BLANKLINE>


Getting Started
---------------

You typically create a new XML document builder by calling the
:func:`xml4h.build` function with the name of the root element::

    >>> root_b = xml4h.build('RootElement')

The function returns a :class:`~xml4h.builder.Builder` object that represents
the *RootElement* and allows you to manipulate this element's attributes
or to add child elements.

Once you have the first builder instance, every action you perform to add
content to the XML document will return another instance of the Builder class::

    >>> # Add attributes to the root element's Builder
    >>> root_b = root_b.attributes({'a': 1, 'b': 2}, c=3)

    >>> root_b  #doctest:+ELLIPSIS
    <xml4h.builder.Builder object ...

The Builder class always represents an underlying element in the DOM. The
:attr:`~xml4h.builder.Builder.dom_element` attribute returns the element node:: 

    >>> root_b.dom_element
    <xml4h.nodes.Element: "RootElement">

    >>> root_b.dom_element.attributes
    <xml4h.nodes.AttributeDict: [('a', '1'), ('b', '2'), ('c', '3')]>

When you add a new child element, the result is a builder instance representing
that child element, *not the original element*::

    >>> child1_b = root_b.element('ChildElement1')
    >>> child2_b = root_b.element('ChildElement2')

    >>> # The element method returns a Builder wrapping the new child element
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
``root_b``, ``child1_b`` and ``child2_b`` to represent builder instances but
this is not necessary. Here is how you can use method-chaining to build the
same document with less code::

    >>> b = (xml4h
    ...     .build('RootElement').attributes({'a': 1, 'b': 2}, c=3)
    ...         .element('ChildElement1').up()  # NOTE the up() method
    ...         .element('ChildElement2')
    ...     )

    >>> print(b.xml_doc(indent=4))
    <?xml version="1.0" encoding="utf-8"?>
    <RootElement a="1" b="2" c="3">
        <ChildElement1/>
        <ChildElement2/>
    </RootElement>
    <BLANKLINE>

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

Without the ``up()`` method, every time you created a child element with the
builder you would end up deeper in the document structure with no way to return
to prior elements to add sibling nodes or hierarchies.

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
   To avoid making subtle errors in your document's structure, we recommend you
   use :meth:`~xml4h.builder.Builder.up` calls to return up one level for every
   :meth:`~xml4h.builder.Builder.element` method (or alias) you call.


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
way the builder doesn't allow:

- The :attr:`~xml4h.builder.Builder.dom_element` attribute returns a builder's
  underlying :class:`~xml4h.nodes.Element`
- The :attr:`~xml4h.builder.Builder.root` attribute returns the document's
  root element.
- The :attr:`~xml4h.builder.Builder.document` attribute returns a builder's
  underlying :class:`~xml4h.nodes.Document`.

See the :ref:`api-nodes` documentation to find out how to work with DOM
element nodes once you get them.


Building on an Existing DOM
---------------------------

When you are building an XML document from scratch you will generally use
the :func:`~xml4h.build` function described in `Getting Started`_. However,
what if you want to add content to a parsed XML document DOM you have already?

To wrap an :class:`~xml4h.nodes.Element` DOM node with a builder you simply
provide the element node to the same ``builder()`` method used previously and
it will do the right thing.

Here is an example of parsing an existing XML document, locating an element
of interest, constructing a builder from that element, and adding some new
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
    >>> b = (lob_builder.attrs(stars=5)
    ...     .elem('Review').t('One of my favourite films!').up())

    >>> # See the results
    >>> print(lob_builder.xml())  # doctest:+ELLIPSIS
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
    >>> print(odd_b.xml_doc(indent=True))
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
    <BLANKLINE>
