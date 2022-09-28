# Analyse GM03 Medium
**Results are available [here](https://docs.google.com/spreadsheets/d/1yfZ_zwq72Q7rIIWJ-HAi1FeMJtv5BqrLHHi9g-z3BmA).**
## Methodology
### Python module
To perform some automatic task (attributes counting), a python module has been created.

**Requirements (python 3)**

* `requests`
* `urllib3`
* `pandas`
* `psycopg2`
* `python-dotenv`
* `lxml`

**Installation**
```python
from AnalyseAttributes import AnalyseAttributes
from AnalyseAttributes import TAG_ATTRIBUTE
from AnalyseAttributes import add_che_extension
from geocat import utils
import pandas as pd
```
---
### GM03 Medium Attributes xpath
The file [GM03_Medium_Xpath.txt](./GM03/GM03_Medium_Xpath.txt) contains all attributes from the GM03 Medium norm given in 
XML-based ISO 19139.che schema format (xpath). This is how the norm is used in geocat.ch. The file has been created manually.

---
### Count GM03 Medium Attributes Usage
For each attribute in the GM03 Medium norm, count the number and percentage of metadata and the number of groups that use it.
Result is saved in the [GM03_Medium_Usage.txt](./GM03/GM03_Medium_Usage.txt).

```python
aa = AnalyseAttributes()

# Read the attributes xpath from GM03 schema and analyse their usage against all metadata
attributes = list()
with open("GM03/GM03_Medium_Xpath.txt", "r") as input:
    for l in input:
        if not l.strip().startswith("#") and l.strip() != '':
            attributes.append(l.strip())

uuids = aa.api.get_uuids_all(). # get all metadata uuid of geocat
attr_usage = aa.count_attribute_usage(attribute=attributes, uuids=uuids). # count attributes

output = open("GM03/GM03_Medium_Usage.txt", "w")

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
```

---
### Attributes that are not in the GM03 Medium norm
Fetch the attributes that are not in the GM03 Medium norm but still widely used by the metadata of geocat.ch. 

To do that, we first retrieve all attributes used by the valid metadata. We don't use the non valid ones (harvested) because 
they potentially contain attributes that are not compatible with ISO schema.
Results are saved in a temporary file `GM03/Valid_Attributes_Usage.txt`

```python
uuids = aa.api.get_uuids_all(valid_only=True)  # only valid metadata

# get attriutes in list of metadata and count their usage against them
attributes = aa.get_attributes_xpath_and_usage(uuids=uuids) 
with open("GM03/Valid_Attributes_Usage.txt", "w") as output:
    output.write("Attribute,Metadata_count,Metadata_%,Group_count\n")
    for key, value in attributes.items():
        output.write(f"{key},{value['metadata_count']},{value['metadata_%']},{value['group_count']}\n")
```

Then, we count their usage by all the metadata in geocat.ch (also the non valid ones).
Results are saved in [Valid_Attributes_Usage.txt](./GM03/Valid_Attributes_Usage.txt).

```python
attributes = list()
with open("GM03/Valid_Attributes_Usage.txt", "r") as input:
    next(input)
    for l in input:
        attributes.append(l.strip().split(",")[0])

uuids = aa.api.get_uuids_all()
attr_usage = aa.count_attribute_usage(attribute=attributes, uuids=uuids)

with open("GM03/Valid_Attributes_Usage_new.txt", "w") as output:
    output.write("Attribute,Metadata_count,Metadata_%,Group_count\n")
    for key, value in attr_usage.items():

        output.write(f"{key},{value['metadata_count']},{value['metadata_%']},{value['group_count']}\n")
```

Then, we filter the attributes that are not in the GM03 Medium Norm. 
This gives the final file [Valid_Attributes_Selection.txt](./GM03/Valid_Attributes_Selection.txt) also available as excel sheet.

```python
gm03_medium = list()

with open("GM03/GM03_Medium_Xpath.txt") as input:
    for l in input:
        if not l.strip().startswith("#") and l.strip != "":
            gm03_medium.append(l.strip())
  
df = pd.read_csv("GM03/Valid_Attributes_Usage_new.txt")
# Extract rows that are not in GM03
filtered_df = df[~df.Attribute.isin(gm03_medium)]
filtered_df.to_csv("GM03/Valid_Attributes_Selection_new.txt",index=False)
```

---
### Attributes from the CHE extension
The GM03 Medium is based on the iso19139 XML schema with an extension of 96 attributes/classes to create a new XML schema: the iso19139.che. If the future of the swiss geometadata norm keeps relying on ISO schema, an objective will be to get rid of custom schema like the current iso19139.che. To do that, it will be necessary to get rid of or replace the custom 96 classes/attributes by attribute and classes available in a standard ISO schema.

Therefore, we analyse the attributes from the CHE extension separately to see if we can delete them or how we can replace them.

The file [CHE_Only_Attributes.txt](./CHE/CHE_Only_Attributes.txt) contains all attributes from the CHE extension given in 
XML-based ISO 19139.che schema format (xpath). The file has been created manually.

---
### Count CHE attributes usage
Results are saved in [CHE_Usage.txt](./CHE/CHE_Usage.txt)

```python
che_attributes = list()
with open("CHE/CHE_Only_Attributes.txt", "r") as input:
    for l in input:
        if l.strip() != '':
            che_attributes.append(l.strip().split(" ")[0])

uuids = aa.api.get_uuids_all()
attr_usage = aa.count_attribute_usage(attribute=che_attributes, uuids=uuids)

output = open("CHE/CHE_Usage.txt", "w")
output.write("Attribute,Label,Description,MD Count,MD %,Group Count\n")

with open("CHE/CHE_Only_Attributes.txt", "r") as input:
    for l in input:
        if l.strip() == "":
            output.write(l)
            output.write("Attribute,Label,Description,MD Count,MD %,Group Count\n")

        else:
            l = l.strip().split(" ")[0]
            output.write(f"{l},,,{attr_usage[l]['metadata_count']},"\
                f"{attr_usage[l]['metadata_%']},{attr_usage[l]['group_count']}\n")

output.close()
```

---
### GM03 Medium Attributes Usage in google sheet
Takes the `GM03/GM03_Medium_Usage.txt` file and add useful information to have a clean file to import into Google sheet 
[GM03_Usage_sheet.txt](./GM03_Usage_sheet.txt). Some information have been added manually in Google sheet.

<details>
    <summary>Show more</summary>
    
```python
output = open("GM03_Usage_sheet.txt", "w")

che_only = list()
with open("CHE/CHE_Only_Attributes.txt", "r") as input:
    for l in input:
        if l.strip() != "":
            che_only.append(l.strip().split(" ")[0])

all_attributes = list()
with open("All_Used_Attributes/Attributes_Xpaths_NonHarvested_Count.txt") as input:
    next(input)
    for l in input:
        all_attributes.append(l.split(",")[0].split("/"))


with open("GM03/GM03_Medium_Usage.txt", "r") as input:
    for l in input:
        if l.strip().startswith("#"):
            output.write(f"# {l.replace('#','').replace('-','')}")
            output.write("Attribute,Label,Description,MD Count,MD %,Group Count,Type,CHE,Core,BGDI,GDB,ODS,Inspire\n")

        elif l.strip().startswith("Attribute"):
            continue

        elif l.strip() == "":
            output.write(l)

        else:
            che = ""
            attr_type = ""
            for i in che_only:
                if i in l.strip():
                    che = "yes"

            last_tag = l.strip().split(",")[0].split("/")[-1]
            if utils.xpath_ns_code2url(last_tag) in TAG_ATTRIBUTE or "Code" in last_tag:
                attribute = "/".join(l.strip().split(",")[0].split("/")[:-1])
                attr_type = last_tag
            else:
                attribute = l.strip().split(",")[0]
                classes = list()
                for i in all_attributes:
                    for j in range(len(i)):
                        if last_tag == i[j]:
                            if j == len(i)-1:
                                if add_che_extension(i[j]) not in classes:
                                    classes.append(add_che_extension(i[j]))
                                    attribute = "/".join(l.strip().split(",")[0].split("/")[:-1])
                            else:                 
                                if add_che_extension(i[j+1]) not in classes:
                                    classes.append(add_che_extension(i[j+1]))

                attr_type = " or ".join(classes)

            output.write(f"{attribute},,,{','.join(l.strip().split(',')[1:])},{attr_type},{che},,,,,\n")

output.close()
```
    
</details>
