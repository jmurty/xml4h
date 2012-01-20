__title__ = 'xml4h'
__version__ = '0.0.1'


from .builder import builder, builder_xmldom, builder_lxml

# Detect which XML libraries are available, we only handle a subset

XML_LIB_PYXML = 'PyXML'
XML_LIB_STANDARD_XML = 'StandardXML'

_XML_LIBRARIES = []
import xml
if xml.__name__ == '_xmlplus':
    # PyXML is installed (augments standard library's xml packages, yuck)
    _XML_LIBRARIES.append(XML_LIB_PYXML)
else:
    _XML_LIBRARIES.append(XML_LIB_STANDARD_XML)


def xml_libs_installed():
    return _XML_LIBRARIES

def is_xml_lib_installed(xml_lib_designator):
    return xml_lib_designator in _XML_LIBRARIES

def is_pyxml_installed():
    return is_xml_lib_installed(XML_LIB_PYXML)
