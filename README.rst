===============================
xml4h: XML for Humans in Python
===============================

*xml4h* is an ISC licensed library for Python to make working with XML
a human-friendly activity.

This library exists because Python is awesome, XML is everywhere, and combining
the two should be a pleasure. With *xml4h*, it can be.


Features
--------

*xml4h* is a simplification layer over existing Python XML processing libraries
such as *lxml* and the *minidom*. It provides:

- a rich pythonic API to traverse and manipulate the XML DOM.
- a document builder to simply and safely construct complex documents with
  minimal code.
- a writer that serialises XML documents with the structure and format that you
  expect, unlike the machine- but not human-friendly output you tend to get
  from other libraries.

The *xml4h* abstraction layer also offers some other benefits, beyond a nice
API and tool set:

- A common interface to different underlying XML libraries, so code written
  against *xml4h* need not be rewritten if you switch implementations.
- You can easily move between *xml4h* and the underlying implementation: parse
  your document using the fastest implementation, manipulate the DOM with
  human-friendly code using *xml4h*, then get back to the underlying
  implementation if you need to.


Installation
------------

Install *xml4h* with pip::

    $ pip install xml4h


Introduction
------------

Here is an example of parsing and reading data from an XML document using
"magic" element and attribute lookups::

    >>> import xml4h
    >>> doc = xml4h.parse('tests/data/monty_python_films.xml')

    >>> for film in doc.MontyPythonFilms.Film[:3]:
    ...     print film['year'], ':', film.Title.text
    1971 : And Now for Something Completely Different
    1974 : Monty Python and the Holy Grail
    1979 : Monty Python's Life of Brian

You can also use a more traditional approach to traverse the DOM::

    >>> for film in doc.child('MontyPythonFilms').children('Film')[:3]:
    ...     print film.attributes['year'], ':', film.children.first.text
    1971 : And Now for Something Completely Different
    1974 : Monty Python and the Holy Grail
    1979 : Monty Python's Life of Brian

The *xml4h* builder makes programmatic document creation simple, with
a method-chaining feature that allows for expressive but sparse code that
mirrors the document itself::

    >>> b = (xml4h.build('MontyPythonFilms')
    ...     .attributes({'source': 'http://en.wikipedia.org/wiki/Monty_Python'})
    ...     .element('Film')
    ...         .attributes({'year': 1971})
    ...         .element('Title')
    ...             .text('And Now for Something Completely Different')
    ...             .up()
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

Pretty-print your XML document with the flexible write() and xml() methods::

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


Why?
----

Python has three popular libraries for working with XML, none of which are
particularly easy to use:

- `xml.dom.minidom <http://docs.python.org/library/xml.dom.minidom.html>`_
  is a light-weight, moderately-featured implementation of the W3C DOM
  that is included in the standard library. Unfortunately the W3C DOM API is
  terrible – the very opposite of pythonic – and the *minidom* does not
  support XPath expressions.
- `xml.etree.ElementTree <http://docs.python.org/library/xml.etree.elementtree.html>`_
  is a fast hierarchical data container that is included in the standard
  library and can be used to represent XML, mostly. The API is fairly pythonic
  and supports XPath, but it lacks some DOM traversal niceties you might
  expect (e.g. to get an element's parent) and when using it you often feel
  like your working with something subtly different from XML, because you are.
- `lxml <http://lxml.de/>`_ is a fast, full-featured XML library with an API
  based on ElementTree but extended. It is your best choice for doing serious
  work with XML in Python but it is not included in the standard library, it
  can be difficult to install, and it gives you the same it's-XML-but-not-quite
  feeling as its ElementTree forebear.

Given these three options it can be difficult to choose which library to use,
especially if you're new to XML processing in Python and haven't already
used (struggled with) any of them.

In the past your best bet would have been to go with *lxml* for the most
flexibility, even though it might be overkill, because at least then you
wouldn't have to rewrite your code if you later find you need XPath support or
powerful DOM traversal methods.

This is where *xml4h* comes in. It provides an abstraction layer over
the existing XML libraries, taking advantage of their power while offering an
improved API and tool set.


This project is heavily inspired by the work of
`Kenneth Reitz <http://kennethreitz.com/pages/open-projects.html>`_ such as
the excellent `Requests HTTP library <http://docs.python-requests.org/>`_.


Development Status: αlphα
-------------------------

Currently *xml4h* includes two adapter implementations that support key XML
processing tasks, using either the *minidom* or *lxml*'s ElementTree libraries.

The project is still at the alpha stage, where I am playing with ideas and
tweaking the APIs to try and get them right before I build out the feature set.

This project is likely to be in flux for a while yet, so be aware that
individual APIs and even broad approaches may change.
