# Analyse GM03 Medium
**Results of the study are available [here](https://docs.google.com/spreadsheets/d/1yfZ_zwq72Q7rIIWJ-HAi1FeMJtv5BqrLHHi9g-z3BmA).**
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
XML-based ISO 19139.che profile format (xpath). This is how the norm is used in geocat.ch. The file has been created manually.

---
### Count GM03 Medium Attributes Usage
For each attribute in the GM03 Medium norm, count the number and percentage of metadata and the number of groups that use it.
Result is saved in the [GM03_Medium_Usage.txt](./GM03/GM03_Medium_Usage.txt)
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

To do that, we first retrieve all attributes used by the metadata
