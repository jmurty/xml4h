import unittest
import re
import xml.dom
from functools import partial

from xml4h import builder, builder_xmldom


class TestBuilderMethods(unittest.TestCase):

    def test_create_invalid_impl(self):
        self.assertRaises(Exception,
            builder_xmldom, ('DocRoot',), dict(impl_name='invalid'))

    def test_create_minidom(self):
        xmlb = builder_xmldom('DocRoot', impl_name='minidom')
        self.assertIsInstance(xmlb.impl_document, xml.dom.minidom.Document)

    def test_create_default(self):
        xmlb = builder('DocRoot')
        self.assertIsInstance(xmlb.impl_document, xml.dom.minidom.Document)


class BaseBuilderNodesTest(object):

    @property
    def my_builder(self):
        raise NotImplementedError()

    def test_element(self):
        xmlb = self.my_builder('DocRoot')
        # Aliases
        self.assertEqual(xmlb.build_element, xmlb.build_elem)
        self.assertEqual(xmlb.build_element, xmlb.build_e)
        # Add elements
        xmlb = (
            self.my_builder('DocRoot')
                .build_e('Deeper')
                .build_e('AndDeeper')
                .build_e('DeeperStill'))
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
        xmlb = (
            self.my_builder('DocRoot')
                .build_e('Deeper')
                .build_e('AndDeeper')
                .build_e('DeeperStill'))
        # Builder node is at DeeperStill element, but we can get to the root
        self.assertEqual('DeeperStill', xmlb.name)
        self.assertEqual('DocRoot', xmlb.root.name)

    def test_up(self):
        xmlb = (
            self.my_builder('DocRoot')
                .build_e('Deeper')
                .build_e('AndDeeper')
                .build_e('DeeperStill'))
        self.assertEqual('DeeperStill', xmlb.name)

        # Can navigate up XML DOM tree one step at a time...
        self.assertEqual('AndDeeper', xmlb.up().name)
        self.assertEqual('Deeper', xmlb.up().up().name)
        self.assertEqual('DocRoot', xmlb.up().up().up().name)
        # ...but not past the root element
        self.assertEqual('DocRoot', xmlb.up().up().up().up().name)

        # Can navigate up by count...
        self.assertEqual('AndDeeper', xmlb.up().name)
        self.assertEqual('Deeper', xmlb.up(2).name)
        self.assertEqual('DocRoot', xmlb.up(3).name)
        # ...but not past the root element
        self.assertEqual('DocRoot', xmlb.up(100).name)

        # Can navigate up to a given element tagname
        self.assertEqual('AndDeeper',
            xmlb.up(to_tagname='AndDeeper').name)
        self.assertEqual('Deeper',
            xmlb.up(to_tagname='Deeper').name)
        self.assertEqual('DocRoot',
            xmlb.up(to_tagname='DocRoot').name)
        # ...but not past the root element if there is no such tagname
        self.assertEqual('DocRoot',
            xmlb.up(to_tagname='NoSuchName').name)

    def test_attributes(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.build_attributes, xmlb.build_attrs)
        self.assertEqual(xmlb.build_attributes, xmlb.build_as)
        # Add attributes
        xmlb = (
            self.my_builder('DocRoot')
              .build_e('Elem1').build_as(x=1).up() # Add a single name/value pair
              .build_e('Elem2').build_as(a='a', b='bee').up() # Add multiple
              .build_e('Elem3').build_as([ # Add list of tuple pairs
                  ('hyphenated-name', 'v2'),
                  ]).up()
              .build_e('Elem4').build_as({ # Add a dictionary
                  'twelve': 3 * 4,
                  }).up()
              # Attributes given in first arg trump same name in kwargs
              .build_e('Elem5').build_as(
                  {'test': 'value-in-first-arg'},
                  test='value-in-kwargs').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1 x="1"/>\n'
            '    <Elem2 a="a" b="bee"/>\n'
            '    <Elem3 hyphenated-name="v2"/>\n'
            '    <Elem4 twelve="12"/>\n'
            '    <Elem5 test="value-in-first-arg"/>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_to_xml(self):
        xmlb = (
            self.my_builder('DocRoot')
                .build_e('Elem1').up()
                .build_e('Elem2'))
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
            '<?xml version="1.0"?>\t'
            '<DocRoot>\t'
            '        <Elem1/>\t'
            '        <Elem2/>\t'
            '</DocRoot>\t',
            xmlb.xml(encoding=None, indent=8, newline='\t'))

    def test_writer(self):
        pass # TODO

    def test_text(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.build_text, xmlb.build_t)
        # Add text values to elements
        xmlb = (
            self.my_builder('DocRoot')
              .build_e('Elem1').build_t('A text value').up()
              .build_e('Elem2').build_t('Seven equals %s' % 7).up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1>A text value</Elem1>\n'
            '    <Elem2>Seven equals 7</Elem2>\n'
            '</DocRoot>\n',
            xmlb.xml())
        # Multiple text nodes, and text node next to nested element
        xmlb = (
            self.my_builder('DocRoot')
              .build_e('Elem1')
                .build_t('First text value')
                .build_t('Second text value').up()
              .build_e('Elem2')
                .build_t('Text')
                .build_e('Nested')
                .build_t('Text in nested').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1>First text valueSecond text value</Elem1>\n'
            '    <Elem2>Text\n'
            '        <Nested>Text in nested</Nested>\n'
            '    </Elem2>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_comment(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.build_comment, xmlb.build_c)
        # Add text values to elements
        xmlb = (
            self.my_builder('DocRoot')
                .build_e('Elem1').build_c('Here is my comment').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1><!--Here is my comment--></Elem1>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_instruction(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(
            xmlb.build_instruction, xmlb.build_processing_instruction)
        self.assertEqual(xmlb.build_instruction, xmlb.build_i)
        # Add text values to elements
        xmlb = (
            self.my_builder('DocRoot').build_i('inst-target', 'inst-data')
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <?inst-target inst-data?>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_namespace(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.set_namespace, xmlb.set_ns)
        # Define namespaces on elements after creation
        xmlb = (
            self.my_builder('DocRoot').set_ns('urn:default')
                .build_e('Elem1').set_ns('urn:elem1').up()
                .build_e('Elem2').set_ns('urn:elem2', prefix='myns').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot xmlns="urn:default">\n'
            '    <Elem1 xmlns="urn:elem1"/>\n'
            '    <Elem2 xmlns:myns="urn:elem2"/>\n'
            '</DocRoot>\n',
            xmlb.xml())
        # Test namespaces work as expected when searching/traversing DOM
        self.assertEqual(1, len(xmlb.find(name='Elem1')))  # Ignore namespace
        self.assertEqual(1, len(xmlb.find(name='Elem1', ns_uri='urn:elem1')))
        self.assertEqual(1, len(xmlb.doc_find(ns_uri='urn:elem1')))
        self.assertEqual(0, len(xmlb.find(name='Elem1', ns_uri='urn:wrong')))
        self.assertEqual(['Elem1'],
            [n.name for n in xmlb.children_in_ns('urn:elem1')])
        # TODO
        #self.assertEqual(['DocRoot', 'Elem2'],
        #    [n.name for n in xmlb.doc_find(ns_uri='urn:default')])
        #self.assertEqual(['Elem2'],
        #    [n.name for n in xmlb.children_in_ns('urn:default')])
        # Set namespaces of elements and attributes on creation
        xmlb = (
            self.my_builder('DocRoot', ns_uri='urn:default')
                .set_ns('urn:custom', 'myns')
                # Elements in default namespace
                .build_e('NSDefaultImplicit').up()
                .build_e('NSDefaultExplicit', ns_uri='urn:default').up()
                # Elements in custom namespace
                .build_e('NSCustomExplicit', ns_uri='urn:custom').up()
                .build_e('myns:NSCustomWithPrefixImplicit').up()
                .build_e('myns:NSCustomWithPrefixExplicit',
                    ns_uri='urn:custom').up()
                # Attributes in namespace
                .build_e('Attrs1')
                    .build_as({'default-ns-implicit': 1})
                    .build_as({'default-ns-explicit': 1},
                        ns_uri='urn:default').up()
                .build_e('Attrs2')
                    .build_as({'custom-ns-explicit': 1},
                        ns_uri='urn:custom')
                    .build_as({'myns:custom-ns-prefix-implicit': 1})
                    .build_as({'myns:custom-ns-prefix-explicit': 1},
                        ns_uri='urn:custom')
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

    def test_cdata(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.build_cdata, xmlb.build_data)
        self.assertEqual(xmlb.build_cdata, xmlb.build_d)
        # Add text values to elements
        xmlb = (
            self.my_builder('DocRoot')
                .build_e('Elem1').build_t('<content/> as text').up()
                .build_e('Elem2').build_d('<content/> as cdata').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1>&lt;content/&gt; as text</Elem1>\n'
            '    <Elem2><![CDATA[<content/> as cdata]]></Elem2>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_element_with_extra_kwargs(self):
        xmlb = (
            self.my_builder('DocRoot')
                # Include attributes
                .build_e('Elem', attributes=[('x', 1)]).up()
                .build_e('Elem', attributes={'my-attribute': 'value'}).up()
                # Include text
                .build_e('Elem', text='Text value').up()
                # Include attributes and text
                .build_e('Elem', attributes={'x': 1}, text='More text').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem x="1"/>\n'
            '    <Elem my-attribute="value"/>\n'
            '    <Elem>Text value</Elem>\n'
            '    <Elem x="1">More text</Elem>\n'
            '</DocRoot>\n',
            xmlb.xml())
        # Insert a new element before another
        xmlb = (
            self.my_builder('DocRoot')
                .build_e('FinalElement')
                .build_e('PenultimateElement', before=True)
                .build_e('ThirdLastElement', before=True)
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <ThirdLastElement/>\n'
            '    <PenultimateElement/>\n'
            '    <FinalElement/>\n'
            '</DocRoot>\n',
            xmlb.xml())

    def test_unicode(self):
        pass # TODO


class TestXmlDomBuilder(BaseBuilderNodesTest, unittest.TestCase):
    '''
    Tests building with the standard library xml.dom module, or with any
    library that augments/clobbers this module.
    '''

    @property
    def my_builder(self):
        return partial(builder_xmldom, impl_name='minidom')

