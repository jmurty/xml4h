======
Parser
======

The *xml4h* parser is a simple wrapper around the parser provided by an
underlying :ref:`XML library implementation <xml-lib-adapters>`.

.. _parser-parse:

Parse function
--------------

To parse XML documents with *xml4h* you feed the :func:`xml4h.parse` function
an XML text document in one of three forms:

- A file-like object::

    >>> import xml4h

    >>> xml_file = open('tests/data/monty_python_films.xml', 'rb')
    >>> doc = xml4h.parse(xml_file)

    >>> doc.MontyPythonFilms
    <xml4h.nodes.Element: "MontyPythonFilms">

- A file path string::

    >>> doc = xml4h.parse('tests/data/monty_python_films.xml')

    >>> doc.root['source']
    'http://en.wikipedia.org/wiki/Monty_Python'

- A string containing literal XML content::

    >>> xml_file = open('tests/data/monty_python_films.xml', 'rb')
    >>> xml_text = xml_file.read()
    >>> doc = xml4h.parse(xml_text)

    >>> len(doc.find('Film'))
    7

.. note:: The :func:`~xml4h.parse` method distinguishes between a file path
          string and an XML text string by looking for a ``<`` character
          in the value.


Stripping of Whitespace Nodes
-----------------------------

By default the *parse* method ignores whitespace nodes in the XML document
-- or more accurately, it does extra work to remove these nodes after the
document has been parsed by the underlying XML library.

Whitespace nodes are rarely interesting, since they are usually the result of
XML content that has been serialized with extra whitespace to make it more
readable to humans.

However if you need to keep these nodes, or if you want to avoid the extra
processing overhead when parsing large documents, you can disable this
feature by passing in the ``ignore_whitespace_text_nodes=False`` flag::

    >>> # Strip whitespace nodes from document
    >>> doc = xml4h.parse('tests/data/monty_python_films.xml')

    >>> # No excess text nodes (XML doc lists 7 films)
    >>> len(doc.MontyPythonFilms.children)
    7
    >>> doc.MontyPythonFilms.children[0]
    <xml4h.nodes.Element: "Film">


    >>> # Don't strip whitespace nodes
    >>> doc = xml4h.parse('tests/data/monty_python_films.xml',
    ...                   ignore_whitespace_text_nodes=False)

    >>> # An extra text node is present
    >>> len(doc.MontyPythonFilms.children)
    8
    >>> doc.MontyPythonFilms.children[0]
    <xml4h.nodes.Text: "#text">
