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

def write(node, writer, encoding='utf-8', indent=0, newline='',
        quote_char='"', omit_declaration=False, _depth=0):

    indent, newline = _sanitize_write_params(indent, newline)

    # Output document declaration if we're outputting the whole doc
    if node.is_document:
        if not omit_declaration:
            writer.write('<?xml version=%s1.0%s' % (quote_char, quote_char))
            if encoding:
                writer.write(' encoding=%s%s%s'
                    % (quote_char, encoding, quote_char))
            writer.write('?>%s' % newline)
        for child in node.children:
            write(child, writer, encoding, indent, newline, quote_char,
                    omit_declaration, _depth)  # Note _depth not incremented
        writer.write(newline)
    elif node.is_document_type:
        writer.write("<!DOCTYPE %s SYSTEM %s%s%s"
            % (node.name, quote_char, node.public_id))
        if node.system_id is not None:
            writer.write(" %s%s%s" % (quote_char, node.system_id, quote_char))
        if node.children:
            writer.write("[")
            for child in node.children:
                write(child, writer, encoding=encoding,
                    indent=indent, newline=newline, quote_char=quote_char,
                    omit_declaration=omit_declaration, _depth=_depth+1)
            writer.write("]")
        writer.write(">")
    elif node.is_text:
        writer.write(_sanitize_write_value(node.value))
    elif node.is_cdata:
        if ']]>' in node.value:
            raise Exception("']]>' is not allowed in CDATA node value")
        writer.write("<![CDATA[%s]]>" % node.value)
    #elif node.is_entity_reference:  # TODO
    elif node.is_entity:
        writer.write(newline + indent * _depth)
        writer.write("<!ENTITY ")
        if node.is_paremeter_entity:
            writer.write('%% ')
        writer.write("%s %s%s%s>"
            % (node.name, quote_char, node.value, quote_char))
    elif node.is_processing_instruction:
        writer.write(newline + indent * _depth)
        writer.write("<?%s %s?>" % (node.target, node.data))
    elif node.is_comment:
        if '--' in node.value:
            raise Exception("'--' is not allowed in COMMENT node value")
        writer.write("<!--%s-->" % node.value)
    elif node.is_notation:
        writer.write(newline + indent * _depth)
        writer.write("<!NOTATION %s" % node.name)
        if node.is_system_identifier:
            writer.write(" system %s%s%s>"
                % (quote_char, node.external_id, quote_char))
        elif node.is_system_identifier:
            writer.write(" system %s%s%s %s%s%s>"
                % (quote_char, node.external_id, quote_char,
                   quote_char, node.uri, quote_char))
    elif node.is_attribute:
        writer.write(" %s=%s" % (node.name, quote_char))
        writer.write(_sanitize_write_value(node.value))
        writer.write(quote_char)
    elif node.is_element:
        # Only need a preceding newline if we're in a sub-element
        if _depth > 0:
            writer.write(newline)
        writer.write(indent * _depth)
        writer.write("<" + node.name)

        for attr in node.attribute_nodes:
            write(attr, writer, encoding=encoding,
                indent=indent, newline=newline, quote_char=quote_char,
                omit_declaration=omit_declaration, _depth=_depth)
        if node.children:
            found_indented_child = False
            writer.write(">")
            for child in node.children:
                write(child, writer, encoding=encoding,
                    indent=indent, newline=newline, quote_char=quote_char,
                    omit_declaration=omit_declaration, _depth=_depth+1)
                if not (child.is_text or child.is_comment or child.is_cdata):
                    found_indented_child = True
            if found_indented_child:
                writer.write(newline + indent * _depth)
            writer.write('</%s>' % node.name)
        else:
            writer.write('/>')
    else:
        raise Exception('write of node %s is not supported' % node.__class__)

