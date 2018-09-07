import unittest

from lxml import etree

from workers.default.xml.xml_validator import validate_xml


class ValidateXMLTest(unittest.TestCase):

    ojs_xml_file = 'test/resources/files/ojs_import.xml'
    ojs_xml_file_faulty = 'test/resources/files/ojs_import_faulty.xml'
    marc_xml_file = 'test/resources/files/marc.xml'
    marc_xml_file_faulty = 'test/resources/files/marc_faulty.xml'
    dtd_file = 'resources/ojs_import.dtd'
    marc_schema_file = 'resources/MARC21slim.xsd'

    def test_validate_xml(self):
        xml_file = self.ojs_xml_file
        validate_xml(xml_file)

    def test_validate_xml_with_DTD(self):
        xml_file = self.ojs_xml_file
        dtd_file = self.dtd_file
        validate_xml(xml_file, dtd_file_path=dtd_file)

    def test_validate_xml_with_schema(self):
        xml_file = self.marc_xml_file
        xml_schema_file = self.marc_schema_file
        validate_xml(xml_file, schema_file_path=xml_schema_file)

    def test_validation_failed_by_syntax(self):
        xml_file = self.ojs_xml_file_faulty
        self.assertRaises(etree.XMLSyntaxError, validate_xml, xml_file)

    def test_validation_failed_by_schema(self):
        xml_file = self.marc_xml_file_faulty
        xml_schema_file = self.marc_schema_file
        self.assertRaises(etree.DocumentInvalid, validate_xml, xml_file,
                          schema_file_path=xml_schema_file)