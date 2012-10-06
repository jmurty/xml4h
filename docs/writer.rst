======
Writer
======

The *xml4h* writer produces serialized XML text documents much as you would
expect, and in that it is a little unlike the writer methods in many of the
Python XML libraries.


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

If you don't supply a writer object to the *write* methods they send output
to :attr:`sys.stdout` by default. To send output to a file, or any other
object that provides a *write* method, you provide the writer to the methods::

    >>> # Write to a file
    >>> with open('/tmp/example.xml', 'wb') as f:
    ...     first_film_elem.write_doc(f)

    >>> # Write to a string (BUT SEE SECTION BELOW...)
    >>> from StringIO import StringIO
    >>> str_writer = StringIO()
    >>> first_film_elem.write_doc(str_writer)
    >>> str_writer.getvalue()  # doctest:+ELLIPSIS
    '<?xml version="1.0" encoding="utf-8"?><MontyPythonFilms source...


Write to a String
-----------------

Because you will often want to generate a string of XML content directly,
*xml4h* includes the convenience methods :meth:`~xml4h.nodes.Node.xml`
and :meth:`~xml4h.nodes.Node.xml_doc` to do this easily.

The :meth:`~xml4h.nodes.Node.xml` method works like the *write* method and
will return a string of XML content including the current node and its
descendants::

    >>> first_film_elem.xml()  # doctest:+ELLIPSIS
    '<Film year="1971">\n    <Title>And Now for Something Completely...

The :meth:`~xml4h.nodes.Node.xml_doc` method works like the *write_doc*
method and returns a string for the whole document::

    >>> first_film_elem.xml_doc()  # doctest:+ELLIPSIS
    '<?xml version="1.0" encoding="utf-8"?>\n<MontyPythonFilms source...

.. note::
   *xml4h* assumes that when you directly generate an XML string you or
   another human will be reading it, so it applies some pretty-print
   formatting options by default.


Format Output
-------------

The *write* and *xml* methods accept a range of formatting options to control
how XML content is serialized. These are only useful if you expect a human
to read the data (poor sod!). If your XML needs to be human-friendly they
can be very helpful.

For the full range of formatting options see the code documentation for
:meth:`~xml4h.nodes.Node.write` et al. but here are some pointers to get
you started:

TODO


Write using the underlying implementation
-----------------------------------------

TODO
