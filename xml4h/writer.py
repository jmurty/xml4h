"""
Writer to serialize XML DOM documents or sections to text.
"""
# This implementation is adapted (heavily) from the standard library method
# xml.dom.minidom.writexml
import six

import codecs

from xml4h import exceptions


def write_node(node, writer, encoding='utf-8', indent=0, newline='',
        omit_declaration=False, node_depth=0, quote_char='"'):
    """
    Serialize an *xml4h* DOM node and its descendants to text, writing
    the output to the given *writer*.

    :param node: the DOM node whose content and descendants will
        be serialized.
    :type node: an :class:`xml4h.nodes.Node` or subclass
    :param writer: a file or stream to which XML text is written.
    :type writer: a file, stream, etc
    :param string encoding: the character encoding for serialized text.
    :param indent: indentation prefix to apply to descendent nodes for
        pretty-printing. The value can take many forms:

        - *int*: the number of spaces to indent. 0 means no indent.
        - *string*: a literal prefix for indented nodes, such as ``\\t``.
        - *bool*: no indent if *False*, four spaces indent if *True*.
        - *None*: no indent.
    :type indent: string, int, bool, or None
    :param newline: the string value used to separate lines of output.
        The value can take a number of forms:

        - *string*: the literal newline value, such as ``\\n`` or ``\\r``.
          An empty string means no newline.
        - *bool*: no newline if *False*, ``\\n`` newline if *True*.
        - *None*: no newline.
    :type newline: string, bool, or None
    :param boolean omit_declaration: if *True* the XML declaration header
        is omitted, otherwise it is included. Note that the declaration is
        only output when serializing an :class:`xml4h.nodes.Document` node.
    :param int node_depth: the indentation level to start at, such as 2 to
        indent output as if the given *node* has two ancestors.
        This parameter will only be useful if you need to output XML text
        fragments that can be assembled into a document.  This parameter
        has no effect unless indentation is applied.
    :param string quote_char: the character that delimits quoted content.
        You should never need to mess with this.
    """
    def _sanitize_write_value(value):
        """Return XML-encoded value."""
        if not value:
            return value
        return (value
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace("\"", "&quot;")
            .replace(">", "&gt;")
            )

    def _write_node_impl(node, node_depth):
        """
        Internal write implementation that does the real work while keeping
        track of node depth.
        """
        # Output document declaration if we're outputting the whole doc
        if node.is_document:
            if not omit_declaration:
                writer.write(
                    '<?xml version=%s1.0%s' % (quote_char, quote_char))
                if encoding:
                    writer.write(' encoding=%s%s%s'
                        % (quote_char, encoding, quote_char))
                writer.write('?>%s' % newline)
            for child in node.children:
                _write_node_impl(child,
                    node_depth)  # node_depth not incremented
            writer.write(newline)
        elif node.is_document_type:
            writer.write("<!DOCTYPE %s SYSTEM %s%s%s"
                % (node.name, quote_char, node.public_id))
            if node.system_id is not None:
                writer.write(
                    " %s%s%s" % (quote_char, node.system_id, quote_char))
            if node.children:
                writer.write("[")
                for child in node.children:
                    _write_node_impl(child, node_depth + 1)
                writer.write("]")
            writer.write(">")
        elif node.is_text:
            writer.write(
                _sanitize_write_value(node.value)
            )
        elif node.is_cdata:
            if ']]>' in node.value:
                raise ValueError("']]>' is not allowed in CDATA node value")
            writer.write(
                "<![CDATA[%s]]>" % node.value
            )
        #elif node.is_entity_reference:  # TODO
        elif node.is_entity:
            writer.write(newline + indent * node_depth)
            writer.write("<!ENTITY ")
            if node.is_paremeter_entity:
                writer.write('%% ')
            writer.write(
                "%s %s%s%s>"
                % (node.name, quote_char, node.value, quote_char)
            )
        elif node.is_processing_instruction:
            writer.write(newline + indent * node_depth)
            writer.write("<?%s %s?>" % (node.target, node.data))
        elif node.is_comment:
            if '--' in node.value:
                raise ValueError("'--' is not allowed in COMMENT node value")
            writer.write("<!--%s-->" % node.value)
        elif node.is_notation:
            writer.write(newline + indent * node_depth)
            writer.write("<!NOTATION %s" % node.name)
            if node.is_system_identifier:
                writer.write(" system %s%s%s>"
                    % (quote_char, node.external_id, quote_char))
            elif node.is_system_identifier:
                writer.write(" system %s%s%s %s%s%s>"
                    % (quote_char, node.external_id, quote_char,
                    quote_char, node.uri, quote_char))
        elif node.is_attribute:
            writer.write(
                " %s=%s" % (node.name, quote_char)
            )
            writer.write(
                _sanitize_write_value(node.value)
            )
            writer.write(quote_char)
        elif node.is_element:
            # Only need a preceding newline if we're in a sub-element
            if node_depth > 0:
                writer.write(newline)
            writer.write(indent * node_depth)
            writer.write("<" + node.name)

            for attr in node.attribute_nodes:
                _write_node_impl(attr, node_depth)
            if node.children:
                found_indented_child = False
                writer.write(">")
                for child in node.children:
                    _write_node_impl(child, node_depth + 1)
                    if not (child.is_text
                            or child.is_comment
                            or child.is_cdata):
                        found_indented_child = True
                if found_indented_child:
                    writer.write(newline + indent * node_depth)
                writer.write('</%s>' % node.name)
            else:
                writer.write('/>')
        else:
            raise exceptions.Xml4hImplementationBug(
                'Cannot write node with class: %s' % node.__class__)

    # Sanitize whitespace parameters
    if indent is True:
        indent = ' ' * 4
    elif indent is False:
        indent = ''
    elif isinstance(indent, int):
        indent = ' ' * indent
    # If indent but no newline set, always apply a newline (it makes sense)
    if indent and not newline:
        newline = True

    if newline is None or newline is False:
        newline = ''
    elif newline is True:
        newline = '\n'

    # If we have a target encoding and are writing to a binary IO stream, wrap
    # the writer with an encoding writer to produce the correct bytes.
    # We detect binary IO streams by:
    # - Python 3: the *absence* of the `encoding` attribute that is present on
    #   `io.TextIOBase`-derived objects
    # - Python 2: the *absence* of the `encode` attribute that is present on
    #   `StringIO` objects
    if (
        encoding
        and not hasattr(writer, 'encoding')
        and not hasattr(writer, 'encode')
    ):
        writer = codecs.getwriter(encoding)(writer)

    # Do the business...
    _write_node_impl(node, node_depth)
