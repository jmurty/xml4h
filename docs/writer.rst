======
Writer
======

The *xml4h* writer produces serialized XML text documents much as you would
expect, and in respect that it is a little unlike the writer methods in some of
the other Python XML libraries.


Write methods
-------------

To write out an XML document with *xml4h* you will generally use the
:meth:`~xml4h.nodes.Node.write` or :meth:`~xml4h.nodes.Node.write_doc` methods
available on any *xml4h* node.

The :meth:`~xml4h.nodes.Node.write` method outputs the current node and any
descendants::

    >>> import xml4h
    >>> doc = xml4h.parse('tests/data/monty_python_films.xml')

    >>> first_film_elem = doc.find('Film')[0]
    >>> first_film_elem.write(indent=True)  # doctest:+ELLIPSIS
    <Film year="1971">
        <Title>And Now for Something Completely Different</Title>
        <Description>A collection of sketches from the first and second...
    </Film>

The :meth:`~xml4h.nodes.Node.write_doc` method outputs the entire document no
matter which node you call it on::

    >>> first_film_elem.write_doc(indent=True)  # doctest:+ELLIPSIS
    <?xml version="1.0" encoding="utf-8"?>
    <MontyPythonFilms source="http://en.wikipedia.org/wiki/Monty_Python">
        <Film year="1971">
            <Title>And Now for Something Completely Different</Title>
            <Description>A collection of sketches from the first and second...
        </Film>
     ...

The *write* methods send output to :attr:`sys.stdout` by default. To send
output to a file, or any other writer-like object, provide the target writer
as an argument::

    >>> # Write to a file
    >>> with open('/tmp/example.xml', 'wb') as f:
    ...     first_film_elem.write_doc(f)

    >>> # Write to a string (BUT SEE SECTION BELOW...)
    >>> from io import BytesIO
    >>> writer = BytesIO()
    >>> first_film_elem.write_doc(writer)
    >>> writer.getvalue()  # doctest:+ELLIPSIS
    b'<?xml version="1.0" encoding="utf-8"?><MontyPythonFilms source...


Write to a String
-----------------

Because you will often want to generate a string of XML content directly,
*xml4h* includes the convenience methods :meth:`~xml4h.nodes.Node.xml`
and :meth:`~xml4h.nodes.Node.xml_doc` to do this easily.

The :meth:`~xml4h.nodes.Node.xml` method works like the *write* method and
will return a string of XML content including the current node and its
descendants::

    >>> print(first_film_elem.xml().decode('utf-8'))  # doctest:+ELLIPSIS
    <Film year="1971">
        <Title>And Now for Something Completely...

The :meth:`~xml4h.nodes.Node.xml_doc` method works like the *write_doc*
method and returns a string for the whole document::

    >>> print(first_film_elem.xml_doc().decode('utf-8'))  # doctest:+ELLIPSIS
    <?xml version="1.0" encoding="utf-8"?>
    <MontyPythonFilms source="http://en.wikipedia.org/wiki/Monty_Python">
        <Film year="1971">
            <Title>And Now for Something Completely Different</Title>
            <Description>A collection of sketches from the first and second...
        </Film>
        ...

.. note::
   *xml4h* assumes that when you directly generate an XML string in this way it
   is intended for human consumption, so it applies pretty-print formatting
   by default.


Format Output
-------------

The *write* and *xml* methods accept a range of formatting options to control
how XML content is serialized. These are useful if you expect a human to read
the resulting data.

For the full range of formatting options see the code documentation for
:meth:`~xml4h.nodes.Node.write` and :meth:`~xml4h.nodes.Node.xml` et al.
but here are some pointers to get you started:

- Set ``indent=True`` to write a pretty-printed XML document with four space
  characters for indentation and ``\n`` for newlines.
- To use a tab character for indenting and ``\r\n`` for indents:
  ``indent='\t', newline='\r\n'``.
- *xml4h* writes *utf-8*-encoded documents by default, to write with a
  different encoding: ``encoding='iso-8859-1'``.
- To avoid outputting the XML declaration when writing a document:
  ``omit_declaration=True``.


Write using the underlying implementation
-----------------------------------------

Because *xml4h* sits on top of an underlying
:ref:`XML library implementation <xml-lib-adapters>` you can use that
library's serialization methods if you prefer, and if you don't mind having
some implementation-specific code.

For example, if you are using *lxml* as the underlying library you can use
its serialisation methods by accessing the implementation node::

    >>> # Get the implementation root node, in this case an lxml node
    >>> lxml_root_node = first_film_elem.root.impl_node
    >>> lxml_root_node.__class__
    <class 'lxml.etree._Element'>

    >>> # Use lxml features as normal; xml4h is no longer in the picture
    >>> from lxml import etree
    >>> xml_str = etree.tostring(
    ...     lxml_root_node, encoding='utf-8', xml_declaration=True, pretty_print=True)
    >>> print(xml_str.decode('utf-8'))  # doctest:+ELLIPSIS
    <?xml version='1.0' encoding='utf-8'?>
    <MontyPythonFilms source="http://en.wikipedia.org/wiki/Monty_Python"><Film year="1971"><Title>And Now for Something Completely Different</Title>
            <Description>A collection of sketches from the first and second...
        </Film>
        <Film year="1974"><Title>Monty Python and the Holy Grail</Title>
            <Description>King Arthur and his knights embark on a low-budget...
        </Film>
        ...

.. note::
   The output from *lxml* is a little quirky, at least on the author's machine.
   Note for example the single-quote characters in the XML declaration, and
   the missing newline and indent before the first ``<Film>`` element. But
   don't worry, that's why you have *xml4h* ;)
