from AnalyseAttributes import AnalyseAttributes
from geopycat import geocat

geocat = geocat(env="prod")
aa = AnalyseAttributes()

headers = {"accept": "application/json", "Content-Type": "application/json"}
groups = geocat.session.get(f"{geocat.env}/geonetwork/srv/api/groups", 
                            headers=headers).json()

readme = open("usageByGroup/README.md", "w")

for group in groups:
    
    uuids = geocat.get_uuids(in_groups=[group["id"]], published_only=True)

    # Read the attributes xpath from GM03 schema and analyse their usage against list of metadata
    attributes = list()
    with open("GM03/GM03_Medium_Xpath.txt", "r") as input:
        for l in input:
            if not l.strip().startswith("#") and l.strip() != '':
                attributes.append(l.strip())

    attr_usage = aa.count_attribute_usage(attribute=attributes, uuids=uuids)

    output = open(f"usageByGroup/GM03_Medium_Usage_{group['id']}.txt", "w")

    with open("GM03/GM03_Medium_Xpath.txt", "r") as input:
        for l in input:
            if l.strip().startswith("#"):
                output.write(l)
                output.write("Attribute,Metadata_count,Metadata_%,Group_count\n")

            elif l.strip() == '':
                output.write(l)
            else:
                output.write(f"{l.strip()},{attr_usage[l.strip()]['metadata_count']},"\
                    f"{attr_usage[l.strip()]['metadata_%']},{attr_usage[l.strip()]['group_count']}\n")

    output.close()

    attributes = aa.get_attributes_xpath_and_usage(uuids=uuids)
    with open(f"usageByGroup/All_Attributes_Usage_{group['id']}.txt", "w") as output:
        output.write("Attribute,Metadata_count,Metadata_%,Group_count\n")
        for key, value in attributes.items():
            output.write(f"{key},{value['metadata_count']},{value['metadata_%']},{value['group_count']}\n")

    readme.write(f"#### {group['label']['eng']}\n")
    readme.write(f"[GM03 medium attributes usage](GM03_Medium_Usage_{group['id']}.txt)<br>\n")
    readme.write(f"[All attributes usage](All_Attributes_Usage_{group['id']}.txt)<br><br>\n")

readme.close()
