xml4h: XML for Humans
=====================

xml4h is an ISC licensed library for Python to make working with XML a
human-friendly activity.

This library exists because Python is awesome, XML is everywhere, and
combining the two should be pleasurable. Right now, it isn't.

This project is heavily inspired by the
`Requests HTTP library <http://docs.python-requests.org/>`.


Development Status
------------------

This project has been somewhat on hiatus due to a lack of time.
It is in no way ready for public consumption or use, but I'm putting it out
there anyway to try and shame myself into working on it more.

TODO
----

Things I'm planning to get to

- Project documentation and code comments
- Support for xpath querying in lxml/ElementTree implementation
- Find a way to make the lxml `nsmap` namespace map mutable, or to fake it?
  This is necessary to properly abstract namespace definition behaviour.
- SAX parsing, done nicely -- Need to figure out what that means...
- Custom nodelist implementations for children, entities, notations, etc to
  allow for human-friendly interactions with lists, such as easily
  add/remove children via the nodelist.
- Complete test coverage and weed out implementation-specific skipped or
  hacky tests
