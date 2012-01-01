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
        # Add elements
        xmlb = builder('DocRoot').e('Deeper').e('AndDeeper').e('DeeperStill')
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Deeper>\n'
            '        <AndDeeper>\n'
            '            <DeeperStill/>\n'
            '        </AndDeeper>\n'
            '    </Deeper>\n'
            '</DocRoot>\n',
            xmlb.xml())

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

        # Can navigate up by count...
        self.assertEqual('AndDeeper', xmlb.up()._element.nodeName)
        self.assertEqual('Deeper', xmlb.up(2)._element.nodeName)
        self.assertEqual('DocRoot', xmlb.up(3)._element.nodeName)
        # ...but not past the root element
        self.assertEqual('DocRoot', xmlb.up(100)._element.nodeName)

        # Can navigate up to a given element tagname
        self.assertEqual('AndDeeper',
            xmlb.up(to_tagname='AndDeeper')._element.nodeName)
        self.assertEqual('Deeper',
            xmlb.up(to_tagname='Deeper')._element.nodeName)
        self.assertEqual('DocRoot',
            xmlb.up(to_tagname='DocRoot')._element.nodeName)
        # ...but not past the root element if there is no such tagname
        self.assertEqual('DocRoot',
            xmlb.up(to_tagname='NoSuchName')._element.nodeName)

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

    def test_text(self):
        # Aliases
        xmlb = builder('DocRoot')
        self.assertEqual(xmlb.text, xmlb.t)
        # Add text values to elements
        xmlb = (
            builder('DocRoot')
              .e('Elem1').t('A text value').up()
              .e('Elem2').t('Seven equals %s' % 7).up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1>\n'
            '        A text value\n'
            '    </Elem1>\n'
            '    <Elem2>\n'
            '        Seven equals 7\n'
            '    </Elem2>\n'
            '</DocRoot>\n',
            xmlb.xml())
        # Multiple text nodes, and text node next to nested element
        xmlb = (
            builder('DocRoot')
              .e('Elem1').t('First text value').t('Second text value').up()
              .e('Elem2').t('Text').e('Nested').t('Text in nested').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1>\n'
            '        First text value\n'
            '        Second text value\n'
            '    </Elem1>\n'
            '    <Elem2>\n'
            '        Text\n'
            '        <Nested>\n'
            '            Text in nested\n'
            '        </Nested>\n'
            '    </Elem2>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_comment(self):
        # Aliases
        xmlb = builder('DocRoot')
        self.assertEqual(xmlb.comment, xmlb.c)
        # Add text values to elements
        xmlb = (
            builder('DocRoot')
                .e('Elem1').c('Here is my comment').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1>\n'
            '        <!--Here is my comment-->\n'
            '    </Elem1>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_instruction(self):
        # Aliases
        xmlb = builder('DocRoot')
        self.assertEqual(xmlb.instruction, xmlb.processing_instruction)
        self.assertEqual(xmlb.instruction, xmlb.i)
        # Add text values to elements
        xmlb = (
            builder('DocRoot').i('inst-target', 'inst-data')
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <?inst-target inst-data?>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_namespace(self):
        # Aliases
        xmlb = builder('DocRoot')
        self.assertEqual(xmlb.namespace, xmlb.ns)
        # Define namespaces on elements after creation
        xmlb = (
            builder('DocRoot').namespace('urn:default')
                .e('Elem1').namespace('urn:elem1').up()
                .e('Elem2').namespace('urn:elem2', prefix='myns').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot xmlns="urn:default">\n'
            '    <Elem1 xmlns="urn:elem1"/>\n'
            '    <Elem2 xmlns:myns="urn:elem2"/>\n'
            '</DocRoot>\n',
            xmlb.xml())
        # Set namespaces of elements and attributes on creation
        xmlb = (
            builder('DocRoot', namespace_uri='urn:default')
                .ns('urn:custom', 'myns')
                # Elements in default namespace
                .e('NSDefaultImplicit').up()
                .e('NSDefaultExplicit', namespace_uri='urn:default').up()
                # Elements in custom namespace
                .e('NSCustomExplicit', namespace_uri='urn:custom').up()
                .e('myns:NSCustomWithPrefixImplicit').up()
                .e('myns:NSCustomWithPrefixExplicit',
                    namespace_uri='urn:custom').up()
                # Attributes in namespace
                .e('Attrs1')
                    .a({'default-ns-implicit': 1})
                    .a({'default-ns-explicit': 1},
                        namespace_uri='urn:default').up()
                .e('Attrs2')
                    .a({'custom-ns-explicit': 1},
                        namespace_uri='urn:custom')
                    .a({'myns:custom-ns-prefix-implicit': 1})
                    .a({'myns:custom-ns-prefix-explicit': 1},
                        namespace_uri='urn:custom')
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot xmlns="urn:default" xmlns:myns="urn:custom">\n'
            '    <NSDefaultImplicit/>\n'
            '    <NSDefaultExplicit xmlns="urn:default"/>\n'
            '    <NSCustomExplicit xmlns="urn:custom"/>\n'
            '    <myns:NSCustomWithPrefixImplicit/>\n'
            '    <myns:NSCustomWithPrefixExplicit xmlns="urn:custom"/>\n'
            '    <Attrs1 default-ns-explicit="1"'
                       ' default-ns-implicit="1"/>\n'
            '    <Attrs2'
                       # TODO Shouldn't this have a namespace prefix?
                       ' custom-ns-explicit="1"'
                       ' myns:custom-ns-prefix-explicit="1"'
                       ' myns:custom-ns-prefix-implicit="1"/>\n'
            '</DocRoot>\n',
            xmlb.xml())
        # TODO Test namespaces work as expected when searching/traversing DOM

# TODO
#    def test_cdata(self):
#        # Aliases
#        xmlb = builder('DocRoot')
#        self.assertEqual(xmlb.cdata, xmlb.data)
#        self.assertEqual(xmlb.cdata, xmlb.d)
#        # Add text values to elements
#        xmlb = (
#            builder('DocRoot')
#                .e('Elem1').t('<content/> as text').up()
#                .e('Elem2').d('<content/> as CDATA').up()
#            )
#        self.assertEqual(
#            '<?xml version="1.0" encoding="utf-8"?>\n'
#            '<DocRoot>\n'
#            '    <Elem1>\n'
#            '        &lt;content&gt; as text\n'
#            '    </Elem1>\n'
#            '    <Elem2>\n'
#            '        <content> as CDATA\n'
#            '    </Elem2>\n'
#            '</DocRoot>\n',
#            xmlb.xml())

    def test_element_with_extra_kwargs(self):
        xmlb = (
            builder('DocRoot')
                # Include attributes
                .e('Elem', attributes=[('x', 1)]).up()
                .e('Elem', attributes={'my-attribute': 'value'}).up()
                # Include text
                .e('Elem', text='Text value').up()
                # Include attributes and text
                .e('Elem', attributes={'x': 1}, text='More text').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem x="1"/>\n'
            '    <Elem my-attribute="value"/>\n'
            '    <Elem>\n'
            '        Text value\n'
            '    </Elem>\n'
            '    <Elem x="1">\n'
            '        More text\n'
            '    </Elem>\n'
            '</DocRoot>\n',
            xmlb.xml())
        # Insert a new element before another
        xmlb = (
            builder('DocRoot')
                .e('FinalElement')
                .e('PenultimateElement', before=True)
                .e('ThirdLastElement', before=True)
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <ThirdLastElement/>\n'
            '    <PenultimateElement/>\n'
            '    <FinalElement/>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_eq(self):
        xmlb1 = builder('DocRoot').e('Elem1').up().e('Elem2')
        xmlb2 = builder('DocRoot').e('Elem1').up().e('Elem2')
        self.assertTrue(xmlb1 == xmlb2)

    def test_unicode(self):
        pass # TODO

