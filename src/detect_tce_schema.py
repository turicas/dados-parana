"""
Utility script to detect schema from a XML from TCE-PR
"""

import argparse
import zipfile
from collections import OrderedDict
from pprint import pprint

import rows
import xmltodict

from spiders.tce_parse_files import parse_xml_from_zip


def detect_schema(filename, internal_name):
    """Detect schema from a TCE-PR XML file (inside a zip archive)"""

    data = parse_xml_from_zip(filename, internal_name)

    field_names = []
    for row in data:
        for field_name in row.keys():
            if field_name not in field_names:
                field_names.append(field_name)

    # Detect field types
    fields = OrderedDict()
    for field_name in field_names:
        field_name = field_name.replace("@", "")
        if field_name.startswith("id"):
            field_type = rows.fields.IntegerField
        else:
            field_type = rows.fields.TextField
        fields[field_name] = field_type
    return fields


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_filename")
    parser.add_argument("internal_name")
    args = parser.parse_args()
    pprint(detect_schema(args.zip_filename, args.internal_name))
