import unittest
import xml.dom

from xml4h import builder, builder_xmldom


class TestXmlDomBuilder(unittest.TestCase):

    def test_create_invalid_impl(self):
        self.assertRaises(Exception,
            builder_xmldom, ('DocRoot',), dict(impl_name='invalid'))

    def test_create_minidom(self):
        xmlb = builder_xmldom('DocRoot', impl_name='minidom')
        self.assertIsInstance(xmlb._document, xml.dom.minidom.Document)

    def test_create_default(self):
        xmlb = builder('DocRoot')
        self.assertIsInstance(xmlb._document, xml.dom.minidom.Document)

    def test_element(self):
        xmlb = builder('DocRoot')
        # Aliases
        self.assertEqual(xmlb.element, xmlb.elem)
        self.assertEqual(xmlb.element, xmlb.e)
        # TODO

    def test_to_xml(self):
        xmlb = builder('DocRoot').e('Elem1').up().e('Elem2')
        # Default printed output is utf-8, and pretty-printed
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1/>\n'
            '    <Elem2/>\n'
            '</DocRoot>\n'
            )
        self.assertEqual(xml, str(xmlb))
        self.assertEqual(xml, unicode(xmlb))
        self.assertEqual(xml, xmlb.xml())
        # Mix it up a bit
        self.assertEqual(
            '<DocRoot>\n'
            '    <Elem1/>\n'
            '    <Elem2/>\n'
            '</DocRoot>\n',
            xmlb.xml(omit_declaration=True))
        self.assertEqual(
            '<?xml version="1.0" encoding="latin1"?>\n'
            '<DocRoot>\n'
            '  <Elem1/>\n'
            '  <Elem2/>\n'
            '</DocRoot>\n',
            xmlb.xml(encoding='latin1', indent=2))
        self.assertEqual(
            '<?xml version="1.0" ?>\t'
            '<DocRoot>\t'
            '        <Elem1/>\t'
            '        <Elem2/>\t'
            '</DocRoot>\t',
            xmlb.xml(encoding=None, indent=8, newline='\t'))

    def test_writer(self):
        pass # TODO

    def test_root(self):
        xmlb = builder('DocRoot').e('Deeper').e('AndDeeper').e('DeeperStill')
        # Builder node is at DeeperStill element, but we can get to the root
        self.assertEqual('DeeperStill', xmlb._element.nodeName)
        self.assertEqual('DocRoot', xmlb.root._element.nodeName)

    def test_up(self):
        xmlb = builder('DocRoot').e('Deeper').e('AndDeeper').e('DeeperStill')
        self.assertEqual('DeeperStill', xmlb._element.nodeName)
        # Can navigate up XML DOM tree one step at a time...
        self.assertEqual('AndDeeper', xmlb.up()._element.nodeName)
        self.assertEqual('Deeper', xmlb.up().up()._element.nodeName)
        self.assertEqual('DocRoot', xmlb.up().up().up()._element.nodeName)
        # ...but not past the root element
        self.assertEqual('DocRoot', xmlb.up().up().up().up()._element.nodeName)
        # Can also navigate up by count...
        self.assertEqual('AndDeeper', xmlb.up()._element.nodeName)
        self.assertEqual('Deeper', xmlb.up(2)._element.nodeName)
        self.assertEqual('DocRoot', xmlb.up(3)._element.nodeName)
        # ...but not past the root element
        self.assertEqual('DocRoot', xmlb.up(100)._element.nodeName)

    def test_attributes(self):
        # Aliases
        xmlb = builder('DocRoot')
        self.assertEqual(xmlb.attributes, xmlb.attrs)
        self.assertEqual(xmlb.attributes, xmlb.a)
        # Add attributes
        xmlb = (
            builder('DocRoot')
              .e('Elem1').a(x=1).up() # Add a single name/value pair
              .e('Elem2').a(a='a', b='bee').up() # Add multiple
              .e('Elem3').a([ # Add list of tuple pairs
                  ('attribute_name', 'v1'),
                  ('hyphenated-name', 'v2'),
                  ]).up()
              .e('Elem4').a({ # Add a dictionary
                  'twelve': 3 * 4,
                  }).up()
              # Attributes given in first arg trump same name in kwargs
              .e('Elem5').a(
                  {'test': 'value-in-first-arg'},
                  test='value-in-kwargs').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1 x="1"/>\n'
            '    <Elem2 a="a" b="bee"/>\n'
            '    <Elem3 attribute_name="v1" hyphenated-name="v2"/>\n'
            '    <Elem4 twelve="12"/>\n'
            '    <Elem5 test="value-in-first-arg"/>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_text(self):
        pass
