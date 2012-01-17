# Adapted from standard library method xml.dom.minidom.writexml

def _sanitize_write_value(value):
    if not value:
        return value
    return (value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace("\"", "&quot;")
        .replace(">", "&gt;")
        )

def _sanitize_write_params(indent='', newline=''):
    if isinstance(indent, int):
        indent = ' ' * indent
    elif indent is True:
        indent = ' ' * 4
    elif indent is False:
        indent = ''

    if newline is True:
        newline = '\n'
    elif newline is False:
        newline = ''

    return (indent, newline)

# TODO: Avoid relying on wrapped version of every node, too inefficient?
def write(node, writer, encoding='utf-8',
        indent=0, newline='', quote_char='"', omit_declaration=False,
        _depth=0):

    indent, newline = _sanitize_write_params(indent, newline)

    # Output document declaration if we're outputting the whole doc
    if node.is_document:
        if not omit_declaration:
            writer.write('<?xml version="1.0"')
            if encoding:
                writer.write(' encoding="%s"' % encoding)
            writer.write('?>%s' % newline)
        for child in node.children:
            write(child, writer, encoding, indent, newline, quote_char,
                    omit_declaration, _depth)  # Note _depth not incremented
    elif node.is_text:
        writer.write(_sanitize_write_value(node.value))
    elif node.is_cdata:
        if ']]>' in node.value:
            raise Exception("']]>' is not allowed in CDATA node value")
        writer.write("<![CDATA[%s]]>" % node.value)
    #elif node.is_entity: # TODO
    elif node.is_processing_instruction:
        writer.write(indent)
        writer.write("<?%s %s?>" % (node.target, node.data))
        writer.write(newline)
    elif node.is_comment:
        if '--' in node.value:
            raise Exception("'--' is not allowed in COMMENT node value")
        writer.write("<!--%s-->" % node.value)
    #elif node.is_notation: # TODO
    elif node.is_element:
        writer.write(indent * _depth)
        writer.write("<" + node.name)

        for attr in node.attributes:
            writer.write(" %s=%s" % (attr.name, quote_char))
            # TODO Handle CDATA nodes (don't munge data)
            writer.write(_sanitize_write_value(attr.value))
            writer.write(quote_char)
        if node.children:
            found_indented_child = False
            last_child_was_indented = False
            writer.write(">")
            for child in node.children:
                if child.is_element or child.is_processing_instruction:
                    if not last_child_was_indented:
                        writer.write(newline)
                    last_child_was_indented = True
                    found_indented_child = True
                else:
                    last_child_was_indented = False
                write(child, writer, encoding=encoding,
                    indent=indent, newline=newline, quote_char=quote_char,
                    omit_declaration=omit_declaration, _depth=_depth+1)
            if found_indented_child:
                writer.write(indent * _depth)
            writer.write('</%s>' % node.name)
        else:
            writer.write('/>')
        writer.write(newline)
    else:
        raise Exception('write of node %s is not supported' % node.__class__)

