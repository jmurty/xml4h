xml4h: XML for Humans
=====================

xml4h is an ISC licensed library for Python to make working with XML a
human-friendly activity.

This library exists because Python is awesome, XML is everywhere, and
combining the two should be a pleasure. Until xml4h, it wasn't.

This project is heavily inspired by the the work of
`Kenneth Reitz <http://kennethreitz.com/pages/open-projects.html>`_ such as
the excellent `Requests HTTP library <http://docs.python-requests.org/>`_.

Why?
----

Python has three popular libraries for working with XML, each which has its
drawbacks:

- `xml.dom.minidom <http://docs.python.org/library/xml.dom.minidom.html>`_
  is a light-weight, moderately-featured implementation of the W3C DOM
  that is included in the standard library. Unfortunately the W3C DOM API is
  terrible -- the very opposite of pythonic -- and the minidom does not
  support XPath expressions.
- `xml.etree.ElementTree <http://docs.python.org/library/xml.etree.elementtree.html>`_
  is a fast hierarchical data container that is included in the standard
  library and can be used to represent XML, mostly. The API is fairly pythonic
  and supports XPath, but it lacks some DOM traversal niceties you might
  expect (e.g. to get an element's parent) and working with it feels like
  your doing something subtely different form XML (because you are).
- `lxml <http://lxml.de/>`_ is a fast, full-featured XML library with an API
  based on ElementTree but extended. It is your best choice for doing serious
  work with XML but it is not included in the standard library, can be
  difficult to install, and suffers from the same it's-XML-but-not-quite
  feeling as its ElementTree forebear.

Given these three options it is hard to choose which library to use,
especially if you're new to XML processing in Python and haven't already
used (struggled with) any of them.

In the past your best bet would have been to go with `lxml` for the most
flexibility, even though it may well be overkill, because at least then
you wouldn't have to rewrite your code if you later find you need XPath
support or powerful DOM traversal methods.

This is where `xml4h` comes in. It provides an abstraction layer over
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
  written against `xml4h` won't need to be rewritten if you switch between
  implementations, such as from minidom to lxml (although not all features
  are available in all implementations).
- Easy movement between `xml4h` and the underlying implementation:
  parse your document using the fastest implementation, manipulate all or
  parts of it with nice code using `xml4h`, then go back to the underlying
  implementation if you need to.
- More to come, see the TODO section

Development Status
------------------

Currently the basic features of two base implementations are available:
minidom and lxml's ElementTree. The project is still at the stage where I am
playing with ideas and tweaking the APIs to try and get them right, before
I move on to the TODO list.

Howver, the project is under very slow development right now, due to my lack
of time. It is very much an alpha, is likely to be in flux for a while yet,
and is in no way ready for production use.

It probably shouldn't even be out in public yet, it isn't fully dressed.
But I'm putting it out there to encourage myself to work on it more, and in
case anyone else would like to start playing with it.

TODO
----

Things I'm planning to get to:

- Write project documentation, code comments, and user guide
- Support for xpath querying in lxml implementation
- Find a way to make the lxml `nsmap` namespace map mutable, or to fake it?
  This is necessary to properly abstract namespace definition behaviour.
- SAX parsing, done nicely -- Need to figure out what that means...
- Custom nodelist implementations for children, entities, notations, etc to
  allow for human-friendly interactions with lists, such as easily
  add/remove children via the nodelist.
- Complete test coverage and weed out implementation-specific skipped or
  hacky tests
