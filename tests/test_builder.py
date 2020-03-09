# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import functools
import os
import six

import xml.dom

import xml4h


class TestBuilderMethods(unittest.TestCase):

    def test_create_minidom(self):
        xmlb = xml4h.build('DocRoot', adapter=xml4h.XmlDomImplAdapter)
        self.assertIsInstance(
            xmlb.dom_element.impl_document, xml.dom.minidom.Document)

    def test_init_class_with_illegal_object(self):
        self.assertRaises(ValueError, xml4h.Builder, 'Bad')

    def test_builder_method_with_illegal_object(self):
        try:
            xml4h.build(123)
        except Exception as ex:
            self.assertEqual(
                xml4h.exceptions.IncorrectArgumentTypeException,
                ex.__class__)
            if six.PY3:
                expected = (
                    "Argument 123 is not one of the expected types: "
                    "[<class 'str'>, <class 'xml4h.nodes.Element'>]"
                )
            else:
                expected = (
                    "Argument 123 is not one of the expected types: "
                    "[<type 'str'>, <class 'xml4h.nodes.Element'>]"
                )
            self.assertEqual(expected, str(ex))


class BaseBuilderNodesTest(object):

    def setUp(self):
        if not self.adapter.is_available():
            self.skipTest('Library for adapter %s is not available'
            % self.adapter)

    @property
    def my_builder(self):
        return functools.partial(xml4h.build, adapter=self.adapter)

    def test_element(self):
        xmlb = self.my_builder('DocRoot')
        # Aliases
        self.assertEqual(xmlb.element, xmlb.elem)
        self.assertEqual(xmlb.element, xmlb.e)
        # Add elements
        xmlb = (
            self.my_builder('DocRoot')
                .e('Deeper')
                .e('AndDeeper')
                .e('DeeperStill'))
        # Check builder's current node is at deepest element
        self.assertEqual('<DeeperStill/>', xmlb.xml())
        # Check builder produces expected XML doc as string
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Deeper>\n'
            '        <AndDeeper>\n'
            '            <DeeperStill/>\n'
            '        </AndDeeper>\n'
            '    </Deeper>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())

    def test_root(self):
        xmlb = (
            self.my_builder('DocRoot')
                .e('Deeper')
                .e('AndDeeper')
                .e('DeeperStill'))
        # Builder node is at DeeperStill element, but we can get to the root
        self.assertEqual('DeeperStill', xmlb.dom_element.name)
        self.assertEqual('DocRoot', xmlb.dom_element.root.name)

    def test_up(self):
        xmlb = (
            self.my_builder('DocRoot')
                .e('Deeper')
                .e('AndDeeper')
                .e('DeeperStill'))
        self.assertEqual('DeeperStill', xmlb.dom_element.name)

        # Can navigate up XML DOM tree one step at a time...
        self.assertEqual('AndDeeper', xmlb.up().dom_element.name)
        self.assertEqual('Deeper', xmlb.up().up().dom_element.name)
        self.assertEqual('DocRoot', xmlb.up().up().up().dom_element.name)
        # ...but not past the root element
        self.assertEqual('DocRoot',
            xmlb.up().up().up().up().dom_element.name)

        # Can navigate up by count...
        self.assertEqual('AndDeeper', xmlb.up().dom_element.name)
        self.assertEqual('Deeper', xmlb.up(2).dom_element.name)
        self.assertEqual('DocRoot', xmlb.up(3).dom_element.name)
        # ...but not past the root element
        self.assertEqual('DocRoot', xmlb.up(100).dom_element.name)

        # Can navigate up to a given element tagname
        self.assertEqual('AndDeeper',
            xmlb.up('AndDeeper').dom_element.name)
        self.assertEqual('Deeper',
            xmlb.up('Deeper').dom_element.name)
        self.assertEqual('DocRoot',
            xmlb.up('DocRoot').dom_element.name)
        # ...but not past the root element if there is no such tagname
        self.assertEqual('DocRoot',
            xmlb.up('NoSuchName').dom_element.name)

    def test_attributes(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.attributes, xmlb.attrs)
        self.assertEqual(xmlb.attributes, xmlb.a)
        # Add attributes
        xmlb = (
            self.my_builder('DocRoot')
              .e('Elem1').attrs(x=1).up()  # Add a single name/value pair
              .e('Elem2').attrs(a='a', b='bee').up()  # Add multiple
              .e('Elem3').attrs([  # Add list of tuple pairs
                  ('hyphenated-name', 'v2'),
                  ]).up()
              .e('Elem4').attrs({  # Add a dictionary
                  'twelve': 3 * 4,
                  }).up()
              # Attributes given in first arg trump same name in kwargs
              .e('Elem5').attrs(
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
            xmlb.dom_element.xml_doc())

    def test_xml(self):
        xmlb = (
            self.my_builder('DocRoot')
                .e('Elem1').up()
                .e('Elem2')
                    .e('Elem3').up())
        # xml() method outputs current node content and descendents only
        self.assertEqual(
            '<Elem2>\n    <Elem3/>\n</Elem2>',
            xmlb.dom_element.xml())
        # Default string output is utf-8, and pretty-printed
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1/>\n'
            '    <Elem2>\n'
            '        <Elem3/>\n'
            '    </Elem2>\n'
            '</DocRoot>\n'
            )
        self.assertEqual(xml, xmlb.dom_element.xml_doc())
        # Mix it up a bit
        self.assertEqual(
            '<DocRoot>\n'
            '    <Elem1/>\n'
            '    <Elem2>\n'
            '        <Elem3/>\n'
            '    </Elem2>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc(omit_declaration=True))
        self.assertEqual(
            '<?xml version="1.0" encoding="latin1"?>\n'
            '<DocRoot>\n'
            '  <Elem1/>\n'
            '  <Elem2>\n'
            '    <Elem3/>\n'
            '  </Elem2>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc(encoding='latin1', indent=2))
        self.assertEqual(
            '<?xml version="1.0"?>\t'
            '<DocRoot>\t'
            '        <Elem1/>\t'
            '        <Elem2>\t'
            '                <Elem3/>\t'
            '        </Elem2>\t'
            '</DocRoot>\t',
            xmlb.dom_element.xml_doc(encoding=None, indent=8, newline='\t'))

    def test_text(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.text, xmlb.t)
        # Add text values to elements
        xmlb = (
            self.my_builder('DocRoot')
              .e('Elem1').t('A text value').up()
              .e('Elem2').t('Seven equals %s' % 7).up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1>A text value</Elem1>\n'
            '    <Elem2>Seven equals 7</Elem2>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())
        # Multiple text nodes, and text node next to nested element
        xmlb = (
            self.my_builder('DocRoot')
              .e('Elem1')
                .t('First text value')
                .t('Second text value').up()
              .e('Elem2')
                .t('Text')
                .e('Nested')
                .t('Text in nested').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1>First text valueSecond text value</Elem1>\n'
            '    <Elem2>Text\n'
            '        <Nested>Text in nested</Nested>\n'
            '    </Elem2>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())

    def test_comment(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.comment, xmlb.c)
        # Add text values to elements
        xmlb = (
            self.my_builder('DocRoot')
                .e('Elem1').c('Here is my comment').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <Elem1><!--Here is my comment--></Elem1>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())

    def test_instruction(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(
            xmlb.instruction, xmlb.processing_instruction)
        self.assertEqual(xmlb.instruction, xmlb.i)
        # Add text values to elements
        xmlb = (
            self.my_builder('DocRoot').i('inst-target', 'inst-data')
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <?inst-target inst-data?>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())

    def test_namespace(self):
        # Define namespaces on elements after creation
        xmlb = (
            self.my_builder('DocRoot', ns_uri='urn:default')
                .e('Elem1', ns_uri='urn:elem1').up()
                .e('Elem2').ns_prefix('myns', 'urn:elem2').up()
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot xmlns="urn:default">\n'
            '    <Elem1 xmlns="urn:elem1"/>\n'
            '    <Elem2 xmlns:myns="urn:elem2"/>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())
        # Test namespaces work as expected when searching/traversing DOM
        self.assertEqual(1, len(xmlb.find(name='Elem1')))  # Ignore namespace
        self.assertEqual(1, len(xmlb.find(name='Elem1', ns_uri='urn:elem1')))
        self.assertEqual(1, len(xmlb.find_doc(ns_uri='urn:elem1')))
        self.assertEqual(0, len(xmlb.find(name='Elem1', ns_uri='urn:wrong')))
        self.assertEqual(['Elem1'],
            [n.name for n in xmlb.dom_element.children(ns_uri='urn:elem1')])
        self.assertEqual(['DocRoot', 'Elem2'],
            [n.name for n in xmlb.find_doc(ns_uri='urn:default')])
        self.assertEqual(['Elem2'],
            [n.name for n in xmlb.dom_element.children(ns_uri='urn:default')])
        # Set namespaces of elements and attributes on creation
        xmlb = (
            self.my_builder('DocRoot', ns_uri='urn:default')
                .ns_prefix('myns', 'urn:custom')
                # Elements in default namespace
                .e('NSDefaultImplicit').up()
                .e('NSDefaultExplicit', ns_uri='urn:default').up()
                # Elements in custom namespace
                .e('NSCustomExplicit', ns_uri='urn:custom').up()
                .e('myns:NSCustomWithPrefixImplicit').up()
                .e('myns:NSCustomWithPrefixExplicit',
                    ns_uri='urn:custom').up()
                # Attributes in namespace
                .e('Attrs1')
                    .attrs({'default-ns-implicit': 1})
                    .attrs({'default-ns-explicit': 1},
                        ns_uri='urn:default').up()
                .e('Attrs2')
                    .attrs({'myns:custom-ns-prefix-implicit': 1})
                    .attrs({'myns:custom-ns-prefix-explicit': 1},
                        ns_uri='urn:custom')
            )
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot xmlns="urn:default" xmlns:myns="urn:custom">\n'
            '    <NSDefaultImplicit/>\n'
            '    <NSDefaultExplicit xmlns="urn:default"/>\n'
            '    <NSCustomExplicit xmlns="urn:custom"/>\n'
            '    <myns:NSCustomWithPrefixImplicit/>\n'
            '    <NSCustomWithPrefixExplicit xmlns="urn:custom"/>\n'
            '    <Attrs1 default-ns-explicit="1"'
                       ' default-ns-implicit="1"/>\n'
            '    <Attrs2'
                       ' myns:custom-ns-prefix-explicit="1"'
                       ' myns:custom-ns-prefix-implicit="1"/>\n'
            '</DocRoot>\n'
        )
        self.assertEqual(xml, xmlb.dom_element.xml_doc())
        # Test namespaces work as expected when searching/traversing DOM
        self.assertEqual(
            ['DocRoot', 'NSDefaultImplicit', 'NSDefaultExplicit',
             'Attrs1', 'Attrs2'],
            [n.name for n in xmlb.find_doc(ns_uri='urn:default')])
        self.assertEqual(
            ['NSCustomExplicit',
             'NSCustomWithPrefixImplicit',
             'NSCustomWithPrefixExplicit'],
            [n.local_name for n in xmlb.find_doc(ns_uri='urn:custom')])
        self.assertEqual(
            ['NSCustomExplicit', 'NSCustomWithPrefixImplicit',
             'NSCustomWithPrefixExplicit'],
            [n.local_name for n in xmlb.find_doc(ns_uri='urn:custom')])
        # Check attribute namespaces
        self.assertEqual(
            [xml4h.nodes.Node.XMLNS_URI, xml4h.nodes.Node.XMLNS_URI],
            [n.namespace_uri for n in xmlb.dom_element.root.attribute_nodes])
        attrs1_elem = xmlb.document.find_first('Attrs1')
        self.assertEqual([None, None],
            [n.namespace_uri for n in attrs1_elem.attribute_nodes])
        attrs2_elem = xmlb.document.find_first('Attrs2')
        self.assertEqual(['urn:custom', 'urn:custom'],
            [n.namespace_uri for n in attrs2_elem.attribute_nodes])

    def test_element_creation_with_namespace(self):
        # Define namespaces on elements using prefixes
        xmlb = (
            self.my_builder('DocRoot', ns_uri='urn:default')
                .ns_prefix('testns', 'urn:test')
                .e('testns:Elem1').up()  # Standard XML-style prefix name
                .e('{urn:test}Elem2').up()  # ElementTree-style prefix URI
                .e('Attrs').attrs({
                    'testns:attrib1': 'value1',
                    '{urn:test}attrib2': 'value2'})
            )
        root = xmlb.dom_element.root
        self.assertEqual('testns', root.find_first(name='Elem1').prefix)
        self.assertEqual('testns', root.find_first(name='Elem2').prefix)
        self.assertEqual(
            'urn:test', root.find_first(name='Elem1').namespace_uri)
        self.assertEqual(
            'urn:test', root.find_first(name='Elem2').namespace_uri)
        self.assertEqual('testns:Elem1', root.find_first(name='Elem1').name)
        self.assertEqual('testns:Elem2', root.find_first(name='Elem2').name)
        attrs_elem = root.find_first(name='Attrs')
        self.assertEqual('Attrs', attrs_elem.name)
        # TODO Allow attrib lookups without namespace prefix?
        self.assertEqual(
            'testns', attrs_elem.attributes.prefix('testns:attrib1'))
        self.assertEqual(
            'testns', attrs_elem.attributes.prefix('testns:attrib2'))
        self.assertEqual(
            'urn:test', attrs_elem.attributes.namespace_uri('testns:attrib1'))
        self.assertEqual(
            'urn:test', attrs_elem.attributes.namespace_uri('testns:attrib2'))
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot xmlns="urn:default" xmlns:testns="urn:test">\n'
            '    <testns:Elem1/>\n'
            '    <testns:Elem2/>\n'
            '    <Attrs testns:attrib1="value1" testns:attrib2="value2"/>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())
        # Attempts to use undefined namespace prefixes will fail
        xmlb = self.my_builder('DocRoot', ns_uri='urn:default')
        self.assertRaises(xml4h.exceptions.UnknownNamespaceException,
            xmlb.e, 'missingns:Elem1')
        self.assertRaises(xml4h.exceptions.UnknownNamespaceException,
            xmlb.attrs, {'missingns:attrib1': 'value1'})
        # Element with literal namespace defn will use the ns as its default
        xmlb = self.my_builder('DocRoot', ns_uri='urn:default')
        xmlb.e('{urn:missing}Elem1')
        self.assertEqual(
            None, xmlb.root.find_first(name='Elem1').prefix)
        self.assertEqual(
            'urn:missing',
            xmlb.root.find_first(name='Elem1').namespace_uri)
        self.assertEqual(
            'urn:missing',
            xmlb.root.find_first(name='Elem1').attributes['xmlns'])
        # Automatically define prefix for attribute with literal namespace
        xmlb.attrs({'{urn:missing2}attrib1': 'value2'})
        self.assertEqual(
            'autoprefix0',
            xmlb.root.attributes.prefix('autoprefix0:attrib1'))
        self.assertEqual(
            'urn:missing2',
            xmlb.root.attributes.namespace_uri('autoprefix0:attrib1'))
        self.assertEqual(
            'urn:missing2',
            xmlb.root.attributes['xmlns:autoprefix0'])
        xmlb.attrs({'{urn:missing3}attrib2': 'value3'})
        self.assertEqual(
            'autoprefix1',
            xmlb.root.attributes.prefix('autoprefix1:attrib2'))
        self.assertEqual(
            'urn:missing3',
            xmlb.root.attributes.namespace_uri('autoprefix1:attrib2'))
        self.assertEqual(
            'urn:missing3',
            xmlb.root.attributes['xmlns:autoprefix1'])

    def test_cdata(self):
        # Aliases
        xmlb = self.my_builder('DocRoot')
        self.assertEqual(xmlb.cdata, xmlb.data)
        self.assertEqual(xmlb.cdata, xmlb.d)
        # Add text values to elements
        xmlb = (
            self.my_builder('DocRoot')
                .e('Elem1').t('<content/> as text').up()
                .e('Elem2').d('<content/> as cdata').up()
            )
        if self.adapter in (xml4h.LXMLAdapter, xml4h.ElementTreeAdapter,
                            xml4h.cElementTreeAdapter):
            # TODO: Make lxml & ElementTree libs support real cdata
            self.assertEqual(
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<DocRoot>\n'
                '    <Elem1>&lt;content/&gt; as text</Elem1>\n'
                '    <Elem2>&lt;content/&gt; as cdata</Elem2>\n'
                '</DocRoot>\n',
                xmlb.dom_element.xml_doc())
        else:
            self.assertEqual(
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<DocRoot>\n'
                '    <Elem1>&lt;content/&gt; as text</Elem1>\n'
                '    <Elem2><![CDATA[<content/> as cdata]]></Elem2>\n'
                '</DocRoot>\n',
                xmlb.dom_element.xml_doc())

    def test_element_with_extra_kwargs(self):
        xmlb = (
            self.my_builder('DocRoot')
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
            '    <Elem>Text value</Elem>\n'
            '    <Elem x="1">More text</Elem>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())
        # Insert a new element before another
        xmlb = (
            self.my_builder('DocRoot')
                .e('FinalElement')
                .e('PenultimateElement', before_this_element=True)
                .e('ThirdLastElement', before_this_element=True)
            )
        self.assertEqual(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<DocRoot>\n'
            '    <ThirdLastElement/>\n'
            '    <PenultimateElement/>\n'
            '    <FinalElement/>\n'
            '</DocRoot>\n',
            xmlb.dom_element.xml_doc())

    def test_unicode(self):
        ns_default = u'urn:默认'
        ns_custom = u'urn:習俗'
        # NOTE lxml doesn't support unicode namespace URIs
        if self.adapter == xml4h.LXMLAdapter:
            ns_default = u'urn:default'
            ns_custom = u'urn:custom'
        xmlb = (
            self.my_builder(u'جذر', ns_uri=ns_default)
                .ns_prefix(u'důl', ns_custom)
                .e(u'důl:ぷㄩƦ').up()
                .e(u'yếutố1')
                    .attrs({u'תכונה': '1'})
                    .up()
                .e(u'yếutố2')
                    .attrs({u'důl:עודתכונה': u'tvö'})
            )
        xml = (
            u'<?xml version="1.0" encoding="utf-8"?>\n'
            u'<جذر xmlns="%(ns_default)s" xmlns:důl="%(ns_custom)s">\n'
            u'    <důl:ぷㄩƦ/>\n'
            u'    <yếutố1 תכונה="1"/>\n'
            u'    <yếutố2 důl:עודתכונה="tvö"/>\n'
            u'</جذر>\n') % {'ns_default': ns_default, 'ns_custom': ns_custom}
        self.assertEqual(xml, xmlb.dom_element.xml_doc())
        doc = xmlb.document
        self.assertEqual(u'جذر', doc.root.name)
        self.assertEqual(ns_default, doc.root.attributes['xmlns'])
        self.assertEqual(ns_custom, doc.root.attributes[u'xmlns:důl'])
        self.assertEqual(3, len(doc.find(ns_uri=ns_default)))
        self.assertEqual(1, len(doc.find(ns_uri=ns_custom)))
        self.assertEqual('1', doc.find_first(u'yếutố1').attributes[u'תכונה'])
        self.assertEqual(
            u'tvö',
            doc.find_first(u'yếutố2').attributes[u'důl:עודתכונה'])

    def test_transplant_and_clone_xml4h_element(self):
        """
        Test transplanting and cloning an xml4h element node from one document
        to another using methods on the xml4h Node.
        """
        cat_b = (
            self.my_builder('Animal')
                .element('Cat')
                    .element('Feature').text('Independent')
            )
        dog_b = (
            self.my_builder('Animal')
                .element('Dog')
                    .element('Feature').text('Loyal')
            )
        horse_b = (
            self.my_builder('Animal')
                .element('Horse')
                    .element('Feature').text('Transport')
            )

        # Transplant an xml4h element node from one doc into another (it is not
        # left in the original document)
        cat_b.document.Animal.transplant_node(dog_b.document.Animal.Dog)
        self.assertEqual(
            '<Animal>'
                '<Cat><Feature>Independent</Feature></Cat>'
                '<Dog><Feature>Loyal</Feature></Dog>'
            '</Animal>',
            cat_b.root.xml(indent=False))
        # Node and descendants are removed from original document
        self.assertEqual('<Animal/>', dog_b.root.xml(indent=False))

        # Clone an xml4h element node from one doc into another (it is left in
        # place in the original document)
        cat_b.document.Animal.clone_node(horse_b.document.Animal.Horse)
        self.assertEqual(
            '<Animal>'
                '<Cat><Feature>Independent</Feature></Cat>'
                '<Dog><Feature>Loyal</Feature></Dog>'
                '<Horse><Feature>Transport</Feature></Horse>'
            '</Animal>',
            cat_b.root.xml(indent=False))
        # Node and descendants remain in original document
        self.assertEqual(
            '<Animal>'
                '<Horse><Feature>Transport</Feature></Horse>'
            '</Animal>',
            horse_b.root.xml(indent=False))

    def test_transplant_and_clone_impl_text_node(self):
        """
        Test transplanting and cloning an implementation Text node from one
        document to another using builder methods.
        """
        cat_b = (
            self.my_builder('Animal')
                .element('Cat')
                    .element('Feature').text('Independent')
            )
        dog_b = (
            self.my_builder('Animal')
                .element('Dog')
                    .element('Feature').text('Loyal')
            )
        horse_b = (
            self.my_builder('Animal')
                .element('Horse')
                    .element('Feature').text('Transport')
            )

        # Transplant an implementation Text node from one doc into another
        cat_feature_b = cat_b
        self.assertEqual('Feature', cat_feature_b.dom_element.name)
        cat_feature_b.transplant(
            dog_b.document.Animal.Dog.Feature.children[0].impl_node) \
            .up().element('X')  # Check method chaining works after transplant
        self.assertEqual(
            '<Animal>'
                '<Cat><Feature>IndependentLoyal</Feature><X/></Cat>'
            '</Animal>',
            cat_b.root.xml(indent=False))
        # Check text node is no longer in original document
        self.assertEqual(
            '<Animal><Dog><Feature/></Dog></Animal>',
            dog_b.root.xml(indent=False))

        # Clone an Text node from one doc into another
        cat_feature_b.clone(
            horse_b.document.Animal.Horse.Feature.children[0].impl_node)
        self.assertEqual(
            '<Animal>'
                '<Cat><Feature>IndependentLoyalTransport</Feature><X/></Cat>'
            '</Animal>',
            cat_b.root.xml(indent=False))
        # Check text node is no longer in original document
        self.assertEqual(
            '<Animal><Horse><Feature>Transport</Feature></Horse></Animal>',
            horse_b.root.xml(indent=False))

    def test_build_monty_python_film_example(self):
        """
        Test production of a simple example XML doc; to be reused as project
        documentation.
        """
        # Create builder with the name of the root element
        b = (self.my_builder('MontyPythonFilms')
            # Assign attributes to the new root element
            .attributes(
                {'source': 'http://en.wikipedia.org/wiki/Monty_Python'})
            # Create a child element
            .element('Film')
                # When an element is added, later method calls apply to it
                .attributes({'year': 1971})
                .element('Title')
                    # Set text content of element with text()
                    .text('And Now for Something Completely Different')
                    # Use up() to perform later actions on parent element
                    .up()
                # Builder methods element(), text() etc. have shorter aliases
                .elem('Description').t(
                    "A collection of sketches from the first and second TV"
                    " series of Monty Python's Flying Circus purposely"
                    " re-enacted and shot for film.").up()
                .up()
            )
        # A builder object can be re-used
        (b.e('Film')
            .attrs(year=1974)
            .e('Title').t('Monty Python and the Holy Grail').up()
            .e('Description').t(
                "King Arthur and his knights embark on a low-budget search"
                " for the Holy Grail, encountering humorous obstacles along"
                " the way. Some of these turned into standalone sketches."
                ).up()
            .up()
        )
        # A builder can be created from any element
        doc_root_elem = b.root
        b = (doc_root_elem.builder
            .e('Film')
                .attrs(year=1979)
                .e('Title').t("Monty Python's Life of Brian").up()
                .e('Description').t(
                    "Brian is born on the first Christmas, in the stable "
                    "next to Jesus'. He spends his life being mistaken "
                    "for a messiah."
                    ).up()
                .up()

            .e('Film')
                .attrs(year=1982)
                .e('Title').t('Monty Python Live at the Hollywood Bowl').up()
                .e('Description').t(
                    "A videotape recording directed by Ian MacNaughton of a"
                    " live performance of sketches. Originally intended for"
                    " a TV/video special. Transferred to 35mm and given a"
                    " limited theatrical release in the US."
                    ).up()
                .up()
            .e('Film')
                .attrs(year=1983)
                .e('Title').t("Monty Python's The Meaning of Life").up()
                .e('Description').t(
                    "An examination of the meaning of life in a series of"
                    " sketches from conception to death and beyond."
                    ).up()
                .up()
            .e('Film')
                .attrs(year=2009)
                .e('Title')
                    .t("Monty Python: Almost the Truth (The Lawyer's Cut)")
                    .up()
                .e('Description').t(
                    "This film features interviews with all the surviving"
                    " Python members, along with archive representation for"
                    " the late Graham Chapman."
                    ).up()
                .up()
            .e('Film')
                .attrs(year=2012)
                .e('Title').t("A Liar's Autobiography: Volume IV").up()
                .e('Description').t(
                    "This is an animated film which is based on the memoir"
                    " of the late Monty Python member, Graham Chapman."
                    ).up()
                .up()
        )
        # Compare output of builder with pre-prepared example document
        example_file_path = os.path.join(
            os.path.dirname(__file__), 'data/monty_python_films.xml')
        expected_xml = open(example_file_path).read()
        self.assertEqual(expected_xml, b.xml_doc(indent=True))


class TestXmlDomBuilder(BaseBuilderNodesTest, unittest.TestCase):
    """
    Tests building with the standard library xml.dom module, or with any
    library that augments/clobbers this module.
    """

    @property
    def adapter(self):
        return xml4h.XmlDomImplAdapter


class TestLXMLEtreeBuilder(BaseBuilderNodesTest, unittest.TestCase):
    """
    Tests building with the lxml (lxml.etree) library.
    """

    @property
    def adapter(self):
        return xml4h.LXMLAdapter


class TestElementTreeBuilder(BaseBuilderNodesTest, unittest.TestCase):
    """
    Test building with the (c)ElementTree library.
    """

    @property
    def adapter(self):
        return xml4h.ElementTreeAdapter


class TestcElementTreeBuilder(BaseBuilderNodesTest, unittest.TestCase):
    """
    Test building with the (c)ElementTree library.
    """

    @property
    def adapter(self):
        return xml4h.cElementTreeAdapter
