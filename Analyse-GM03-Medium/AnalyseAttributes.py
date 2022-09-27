from lxml import etree
import xml.etree.ElementTree as ET
import pandas as pd
from geocat.geocat import GeocatAPI
from geocat import utils 

# List of tag that correspond to an attribute (i.e. value of tag can be edited, not only for xml 
# structure purpose).
# Comes from the method get_attributes_tag
TAG_ATTRIBUTE = [
    "{http://www.isotc211.org/2005/gco}CharacterString",
    "{http://www.isotc211.org/2005/gco}DateTime",
    "{http://www.isotc211.org/2005/gco}Date",
    "{http://www.isotc211.org/2005/gco}Decimal",
    "{http://www.isotc211.org/2005/gco}Integer",
    "{http://www.isotc211.org/2005/gco}ScopedName",
    "{http://www.isotc211.org/2005/gco}Distance",
    "{http://www.isotc211.org/2005/gco}Boolean",
    "{http://www.isotc211.org/2005/gco}RecordType",
    "{http://www.isotc211.org/2005/gco}LocalName",
    "{http://www.isotc211.org/2005/gco}Record",
    "{http://www.isotc211.org/2005/gco}Real",
    "{http://www.isotc211.org/2005/gco}Measure",
    "{http://www.isotc211.org/2005/gmd}LocalisedCharacterString",
    "{http://www.isotc211.org/2005/gmd}MD_PixelOrientationCode",
    "{http://www.isotc211.org/2005/gmd}URL",
    "{http://www.isotc211.org/2005/gmd}MD_TopicCategoryCode",
    "{http://www.opengis.net/gml/3.2}posList",
    "{http://www.opengis.net/gml/3.2}beginPosition",
    "{http://www.opengis.net/gml/3.2}timePosition",
    "{http://www.opengis.net/gml/3.2}endPosition",
    "{http://www.opengis.net/gml/3.2}duration",
    "{http://www.geocat.ch/2008/che}LocalisedURL",
    "{http://www.isotc211.org/2005/gmx}Anchor",
    "{http://www.isotc211.org/2005/gmx}MimeFileType",
    "{http://www.isotc211.org/2005/gts}TM_PeriodDuration"
]

GM03_CLASSES = [
    "che:CHE_MD_DataIdentification",
    "gmd:MD_BrowseGraphic",
    "gmd:MD_Keywords",
    "gmd:MD_RepresentativeFraction",
    "gmd:MD_Resolution",
    "gmd:MD_Usage",
    "che:CHE_SV_ServiceIdentification",
    "srv:SV_OperationMetadata",
    "srv:SV_CoupledResource",
    "gml:CodeType",
    "gmd:MD_Constraints",
    "che:CHE_MD_LegalConstraints",
    "gmd:MD_SecurityConstraints",
    "gmd:DQ_DataQuality",
    "gmd:LI_Lineage",
    "gmd:LI_ProcessStep",
    "gmd:LI_Source",
    "gmd:DQ_Scope",
    "gmd:MD_ScopeDescription",
    "gmd:DQ_DomainConsistency",
    "gmd:DQ_ConformanceResult",
    "che:CHE_MD_MaintenanceInformation",
    "che:CHE_MD_ArchiveConcept",
    "che:CHE_MD_HistoryConcept",
    "gmd:MD_GridSpatialRepresentation",
    "gmd:MD_VectorSpatialRepresentation",
    "gmd:MD_Dimension",
    "gmd:MD_GeometricObjects",
    "gmd:MD_ReferenceSystem",
    "che:CHE_MD_FeatureCatalogueDescription",
    "che:CHE_MD_CoverageDescription",
    "che:attribute",
    "che:CHE_MD_Class",
    "che:CHE_MD_PortrayalCatalogueReference",
    "gmd:MD_Distribution",
    "gmd:MD_DigitalTransferOptions",
    "gmd:MD_Distributor",
    "gmd:MD_Format",
    "gmd:MD_Medium",
    "gmd:MD_StandardOrderProcess",
    "gmd:CI_OnlineResource",
    "che:CHE_MD_Revision",
    "che:CHE_MD_Legislation",
    "gmd:EX_Extent",
    "gmd:EX_BoundingPolygon",
    "gmd:EX_GeographicBoundingBox",
    "gmd:EX_TemporalExtent",
    "gml:TimePeriod",
    "gmd:CI_Citation",
    "gmd:CI_Date",
    "che:CHE_CI_ResponsibleParty",
    "gmd:CI_Contact",
    "che:CHE_CI_Address",
    "che:CHE_CI_Telephone",
    "gmd:MD_Identifier",
    "gmd:RS_Identifier",
]


class AnalyseAttributes:
    """
    Class to analyse attributes usage of the GM03 medium norm in geocat.ch
    """
    def __init__(self):
        self.api = GeocatAPI(env='prod')

    def get_attributes_tag(self, uuids: list) -> dict:
        """
        Get all editable tag name (i.e. Attribute) from list of metadata uuid.

        Return:
            A dict {tag: uuid}. For each tag name, the first metadata UUID where it was found 
            is given (to check if the tag is really an attribute or not).
        """

        tags = {}

        print(f"Get Attributes Tags from Metadata : ", end="\r")

        count = 0
        for uuid in uuids:
            metadata = self.api.get_metadata_from_mef(uuid=uuid)

            count += 1

            if metadata is None:
                continue

            xmlstring = etree.fromstring(metadata)
            xmlroot = xmlstring.getroottree()

            for e in xmlroot.iter():
                if e.text is not None and "\n" not in e.text:

                    try:
                        path = xmlroot.getelementpath(e)
                    except ValueError:
                        pass
                    else:
                        for i in range(100):
                            path = path.replace(f"[{i}]", "")

                        path = path.split("/{")[-1]
                        path = "{" + path

                        if path not in tags:
                            tags[path] = uuid

            print(f"Get Attributes Tags from Metadata : {round((count / len(uuids)) * 100, 1)}%", end="\r")
        print(f"Get Attributes Tags from Metadata : {utils.okgreen('Done')}")

        return tags

    def get_attributes_xpath_and_usage(self, uuids: list) -> dict:
        """
        Get a list of attributes xpath from a list of metadata uuid. Count their usage against the 
        same list of metadata. Attributes are aggregated according to the GM03 classes.

        Returns:
            Python dictionnary:
                {
                    attribute_1: {metadata_count: str, metadata_%: str, group_count: str},
                    attribute_2: {metadata_count: str, metadata_%: str, group_count: str}.
                    ...
                }
        """

        output = dict()

        print(f"Get Attributes Xpath from Metadata : ", end="\r")

        count = 0
        for uuid in uuids:
            metadata = self.api.get_metadata_from_mef(uuid=uuid)

            count += 1

            if metadata is None:
                continue

            group_id = self.api.get_metadata_group(uuid=uuid)

            xmlstring = etree.fromstring(metadata)
            xmlroot = xmlstring.getroottree()
            xpath_metadata = list()

            for e in xmlroot.iter():
                if (e.text is not None and "\n" not in e.text) or ("codeList" in e.attrib and "codeListValue" in e.attrib):

                    try:
                        path = utils.xpath_ns_url2code(xmlroot.getelementpath(e))
                    except:
                        continue

                    path = add_che_extension(path)

                    for i in range(150):
                        path = path.replace(f"[{i}]", "")

                    start = 0
                    tags = path.split("/")
                    for i in range(len(tags)):
                        if tags[i] in GM03_CLASSES:
                            
                            to_add = "/".join(tags[start:i])
                            if start == 0:
                                to_add = f"che:CHE_MD_Metadata/{to_add}"
                            
                            if to_add not in xpath_metadata:
                                xpath_metadata.append(to_add)

                            start = i

                        if i+1 == len(tags):
                            to_add = "/".join(tags[start:])
                            if to_add not in xpath_metadata:
                                xpath_metadata.append(to_add)                            

            print(f"Get Attributes Xpath from Metadata : {round((count / len(uuids)) * 100, 1)}%", end="\r")

            for attribute in xpath_metadata:
                if attribute not in output:
                    output[attribute] = {"metadata_count": 1, "metadata_%": 0, "group_count": list()}
                    if group_id is not None:
                        output[attribute]["group_count"].append(group_id)
                else:
                    output[attribute]["metadata_count"] += 1
                    if group_id is not None:
                        if group_id not in output[attribute]["group_count"]:
                            output[attribute]["group_count"].append(group_id)

        for key, value in output.items():
            output[key]["group_count"] = len(value["group_count"])
            output[key]["metadata_%"] = round((value["metadata_count"]/len(uuids))*100, 1)

        print(f"Get Attributes Xpath from Metadata : {utils.okgreen('Done')}")

        return output

    def count_attribute_usage(self, attribute: list, uuids: list) -> dict:
        """
        For each attribute given in the list, count the number of metadata 
        from the given metatdata uuids list and the number of group that use the attribute.  

        Returns:
            Python dictionnary:
                {
                    attribute_1: {metadata_count: str, metadata_%: str, group_count: str},
                    attribute_2: {metadata_count: str, metadata_%: str, group_count: str}.
                    ...
                }
        """

        output = {}

        for xpath in attribute:
            output[xpath] = {"metadata_count": 0, "metadata_%": 0, "group_count": list()}

        print(f"Counting attributes usage in Metadata : ", end="\r")
        count = 0
        
        for uuid in uuids:
            metadata = self.api.get_metadata_from_mef(uuid=uuid)

            count += 1

            if metadata is None:
                continue

            xmlroot = ET.fromstring(metadata)
            group_id = self.api.get_metadata_group(uuid=uuid)

            for xpath in attribute:

                # If the attribute xpath starts from the metadata root, we need to erase the root
                # tag for the findall method
                if xpath.split("/")[0] == "che:CHE_MD_Metadata" or \
                    xpath.split("/")[0] == "gmd:MD_Metadata":

                    # Systemically search for xpath with and without che extension
                    search_xpath = "/".join(xpath.split("/")[1:])
                    search_xpath_noche = remove_che_extension(search_xpath)

                    if len(xmlroot.findall(f"./{utils.xpath_ns_code2url(search_xpath)}")) > 0 or \
                        len(xmlroot.findall(f"./{utils.xpath_ns_code2url(search_xpath_noche)}")) > 0:
                        output[xpath]["metadata_count"] += 1

                        if group_id is not None:
                            if group_id not in output[xpath]["group_count"]:
                                output[xpath]["group_count"].append(group_id)
                        
                else:
                    xpath_noche = remove_che_extension(xpath)

                    if len(xmlroot.findall(f".//{utils.xpath_ns_code2url(xpath)}")) > 0 or \
                        len(xmlroot.findall(f".//{utils.xpath_ns_code2url(xpath_noche)}")) > 0:
                        output[xpath]["metadata_count"] += 1

                        if group_id is not None:
                            if group_id not in output[xpath]["group_count"]:
                                output[xpath]["group_count"].append(group_id)                   

            print(f"Counting attributes usage in Metadata : {round((count / len(uuids)) * 100, 1)}%", end="\r")

        for key, value in output.items():
            output[key]["group_count"] = len(value["group_count"])
            output[key]["metadata_%"] = round((value["metadata_count"]/len(uuids))*100, 1)
        
        print(f"Counting attributes usage in Metadata : {utils.okgreen('Done')}")

        return output


def add_che_extension(xpath: str):

    xpath_list = xpath.split("/")
    for i in range(len(xpath_list)):
        if xpath_list[i] == "gmd:CI_ResponsibleParty":
            xpath_list[i] = "che:CHE_CI_ResponsibleParty"

        elif xpath_list[i] == "gmd:CI_Address":
            xpath_list[i] = "che:CHE_CI_Address"

        elif xpath_list[i] == "gmd:CI_Telephone":
            xpath_list[i] = "che:CHE_CI_Telephone"

        elif xpath_list[i] == "gmd:MD_LegalConstraints":
            xpath_list[i] = "che:CHE_MD_LegalConstraints"

        elif xpath_list[i] == "gmd:MD_DataIdentification":
            xpath_list[i] = "che:CHE_MD_DataIdentification"

        elif xpath_list[i] == "gmd:MD_MaintenanceInformation":
            xpath_list[i] = "che:CHE_MD_MaintenanceInformation"

        elif xpath_list[i] == "gmd:MD_FeatureCatalogueDescription":
            xpath_list[i] = "che:CHE_MD_FeatureCatalogueDescription"

        elif xpath_list[i] == "gmd:MD_PortrayalCatalogueReference":
            xpath_list[i] = "che:CHE_MD_PortrayalCatalogueReference"

        elif xpath_list[i] == "gmd:MD_CoverageDescription":
            xpath_list[i] = "che:CHE_MD_CoverageDescription"

        elif xpath_list[i] == "gmd:MD_ImageDescription":
            xpath_list[i] = "che:CHE_MD_ImageDescription"            

        elif xpath_list[i] == "srv:SV_ServiceIdentification":
            xpath_list[i] = "che:CHE_SV_ServiceIdentification"

    return "/".join(xpath_list)

def remove_che_extension(xpath: str):

    xpath_list = xpath.split("/")
    for i in range(len(xpath_list)):
        if xpath_list[i] == "che:CHE_CI_ResponsibleParty":
            xpath_list[i] = "gmd:CI_ResponsibleParty"

        elif xpath_list[i] == "che:CHE_CI_Address":
            xpath_list[i] = "gmd:CI_Address"

        elif xpath_list[i] == "che:CHE_CI_Telephone":
            xpath_list[i] = "gmd:CI_Telephone"

        elif xpath_list[i] == "che:CHE_MD_LegalConstraints":
            xpath_list[i] = "gmd:MD_LegalConstraints"

        elif xpath_list[i] == "che:CHE_MD_DataIdentification":
            xpath_list[i] = "gmd:MD_DataIdentification"

        elif xpath_list[i] == "che:CHE_MD_MaintenanceInformation":
            xpath_list[i] = "gmd:MD_MaintenanceInformation"

        elif xpath_list[i] == "che:CHE_MD_FeatureCatalogueDescription":
            xpath_list[i] = "gmd:MD_FeatureCatalogueDescription"

        elif xpath_list[i] == "che:CHE_MD_PortrayalCatalogueReference":
            xpath_list[i] = "gmd:MD_PortrayalCatalogueReference"

        elif xpath_list[i] == "che:CHE_MD_CoverageDescription":
            xpath_list[i] = "gmd:MD_CoverageDescription"

        elif xpath_list[i] == "che:CHE_MD_ImageDescription":
            xpath_list[i] = "gmd:MD_ImageDescription"            

        elif xpath_list[i] == "che:CHE_SV_ServiceIdentification":
            xpath_list[i] = "srv:SV_ServiceIdentification"

    return "/".join(xpath_list)