=====================
xml4h: XML for Humans
=====================

xml4h is an ISC licensed library for Python to make working with XML a
human-friendly activity.

This library exists because Python is awesome, XML is everywhere, and
combining the two should be a pleasure. With xml4h, it can be.


Introduction
------------

Here is an example of parsing and reading data from an XML document using
"magic" element and attribute lookups:

::

    >>> import xml4h

    >>> doc = xml4h.parse('tests/data/monty_python_films.xml')
    >>> for film in doc.MontyPythonFilms.Film[:3]:
    ...     print film['year'], ':', film.Title.text
    1971 : And Now for Something Completely Different
    1974 : Monty Python and the Holy Grail
    1979 : Monty Python's Life of Brian

You can also use a more traditional approach to traverse the DOM:

::

    >>> for film in doc.find('Film')[:3]:
    ...     print film.attributes['year'], ':', film.children[0].text
    1971 : And Now for Something Completely Different
    1974 : Monty Python and the Holy Grail
    1979 : Monty Python's Life of Brian

With xml4h you can build XML documents with a method-chaining approach that
needs minimal syntax and permits a code structure that mirrors the
document itself:

::

    >>> # Create builder with the name of the root element
    >>> b = (xml4h.build('MontyPythonFilms')
    ...     # Assign attributes to the new root element
    ...     .attributes({'source': 'http://en.wikipedia.org/wiki/Monty_Python'})
    ...     # Create a child element
    ...     .element('Film')
    ...         # When an element is added, later method calls apply to it
    ...         .attributes({'year': 1971})
    ...         .element('Title')
    ...             # Set text content of element with text()
    ...             .text('And Now for Something Completely Different')
    ...             # Use up() to perform later actions on parent element
    ...             .up()
    ...         # Builder methods element(), text() etc. have shorter aliases
    ...         .elem('Description').t(
    ...             "A collection of sketches from the first and second TV"
    ...             " series of Monty Python's Flying Circus purposely"
    ...             " re-enacted and shot for film.").up()
    ...         .up()
    ...     )

    >>> # A builder object can be re-used
    >>> b = (b.e('Film')
    ...     .attrs(year=1974)
    ...     .e('Title').t('Monty Python and the Holy Grail').up()
    ...     .e('Description').t(
    ...         "King Arthur and his knights embark on a low-budget search"
    ...         " for the Holy Grail, encountering humorous obstacles along"
    ...         " the way. Some of these turned into standalone sketches."
    ...         ).up()
    ...     .up()
    ... )

Pretty-print your XML document with the flexible write() method:

::

    >>> b.write_doc(indent=4, newline=True) # doctest: +ELLIPSIS
    <?xml version="1.0" encoding="utf-8"?>
    <MontyPythonFilms source="http://en.wikipedia.org/wiki/Monty_Python">
        <Film year="1971">
            <Title>And Now for Something Completely Different</Title>
            <Description>A collection of sketches from ...</Description>
        </Film>
        <Film year="1974">
            <Title>Monty Python and the Holy Grail</Title>
            <Description>King Arthur and his knights embark ...</Description>
        </Film>
    </MontyPythonFilms>


This project is heavily inspired by the work of
`Kenneth Reitz <http://kennethreitz.com/pages/open-projects.html>`_ such as
the excellent `Requests HTTP library <http://docs.python-requests.org/>`_.


Why?
----

Python has three popular libraries for working with XML, each of which has its
drawbacks:

- `xml.dom.minidom <http://docs.python.org/library/xml.dom.minidom.html>`_
  is a light-weight, moderately-featured implementation of the W3C DOM
  that is included in the standard library. Unfortunately the W3C DOM API is
  terrible – the very opposite of pythonic – and the minidom does not
  support XPath expressions.
- `xml.etree.ElementTree <http://docs.python.org/library/xml.etree.elementtree.html>`_
  is a fast hierarchical data container that is included in the standard
  library and can be used to represent XML, mostly. The API is fairly pythonic
  and supports XPath, but it lacks some DOM traversal niceties you might
  expect (e.g. to get an element's parent) and working with it feels like
  your doing something subtly different form XML (because you are).
- `lxml <http://lxml.de/>`_ is a fast, full-featured XML library with an API
  based on ElementTree but extended. It is your best choice for doing serious
  work with XML in Python, but it is not included in the standard library, can
  be difficult to install, and gives you the same it's-XML-but-not-quite
  feeling as its ElementTree forebear.

Given these three options it is hard to choose which library to use,
especially if you're new to XML processing in Python and haven't already
used (struggled with) any of them.

In the past your best bet would have been to go with *lxml* for the most
flexibility, even though it may well be overkill, because at least then
you wouldn't have to rewrite your code if you later find you need XPath
support or powerful DOM traversal methods.

This is where *xml4h* comes in. It provides an abstraction layer over
the existing XML libraries, taking advantage of their power while offering
the following improvements:

- A richer, W3C-like yet pythonic API for DOM traversal and manipulation.
- A document builder that makes it simple to safely construct complex
  documents with very little code; no more string concatenation and crossed
  fingers.
- Write XML documents you have constructed and see in the output a
  structure and format that you expect, unlike the machine- but
  not human-friendly output you tend to get from the base libraries.
- A common interface that masks the underlying implementations. Code
  written against *xml4h* need not be rewritten if you switch between
  implementations, such as from minidom to lxml (although not all
  features  are available in all implementations).
- Easy movement between *xml4h* and the underlying implementation:
  parse your document using the fastest implementation, manipulate all or
  parts of it with nice code using *xml4h*, then go back to the underlying
  implementation if you need to.
- More to come, see the TODO section


Development Status
------------------

Currently the basic features of two base implementations are available:
*minidom* and *lxml*'s ElementTree. The project is still at the stage where
I am playing with ideas and tweaking the APIs to try and get them right,
before I move on to the TODO list.

This project is an alpha and is likely to be in flux for a while yet,
so be aware that individual APIs and even broad approaches may change.


TODO
----

- Write project documentation, code comments, and user guide
- Add implementation of standard library's (c)ElementTree (if plausible) so
  XPath is available to all users without installing the extra *lxml* library.
- Proper support for more esoteric node types: DocumentType, DocumentFragment,
  Notation, Entity, EntityReference
- Find a way to make the *lxml* ``nsmap`` namespace map mutable, or to fake it?
  This is necessary to properly abstract namespace definition behaviour.
- SAX parsing, done nicely -- Need to figure out what that means...
- Improve NodeList implementations for children, entities, notations, etc to
  allow for human-friendly interactions with lists, such as easily
  add/remove document nodes via the nodelist.
- Complete test coverage and weed out implementation-specific skipped or
  hacky tests
