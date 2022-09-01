#!/usr/bin/env python3
import argparse
from datetime import datetime
import xml.etree.ElementTree as ET


def merge_results(input_files, output_file, classname_prefix=None):
    errors = 0
    failures = 0
    skipped = 0
    tests = 0
    time = 0.0
    hostname = ""
    cases = []

    for file_name in input_files:
        tree = ET.parse(file_name)
        root = tree.getroot()

        # find the "testsuite" element and get its attributes
        testsuite = root[0].attrib
        if "errors" in testsuite:
            errors += int(testsuite["errors"])
        if "failures" in testsuite:
            failures += int(testsuite["failures"])
        if "skipped" in testsuite:
            skipped += int(testsuite["skipped"])
        if "tests" in testsuite:
            tests += int(testsuite["tests"])
        if "time" in testsuite:
            time += float(testsuite["time"])
        if "hostname" in testsuite:
            hostname = str(testsuite["hostname"])

        # append all tests cases under "testsuite" element
        cases.append(list(root)[0])

    # create a new tree with the test cases and results summary
    testsuites = ET.Element("testsuites")
    testsuite = ET.Element("testsuite")
    testsuites.append(testsuite)
    testsuite.attrib["name"] = "pytest"
    testsuite.attrib["errors"] = f"{errors}"
    testsuite.attrib["failures"] = f"{failures}"
    testsuite.attrib["skipped"] = f"{skipped}"
    testsuite.attrib["tests"] = f"{tests}"
    testsuite.attrib["time"] = f"{time}"
    testsuite.attrib["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    testsuite.attrib["hostname"] = f"{hostname}"

    for case in cases:
        if classname_prefix is not None:
            for i in case:
                old_classname = i.attrib["classname"]
                new_classname = f"{classname_prefix}.{old_classname}"
                i.attrib["classname"] = new_classname
        testsuite.extend(case)
    new_tree = ET.ElementTree(testsuites)

    # make it pretty
    ET.indent(new_tree, space="\t", level=0)

    # write to the output file
    new_tree.write(output_file, encoding="utf8", method="xml")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=argparse.FileType("r"), nargs="+")
    parser.add_argument("output", type=argparse.FileType("wb"))
    parser.add_argument(
        "--classname", required=False, help="append a prefix to test's classname"
    )
    args = parser.parse_args()

    merge_results(args.input, args.output, args.classname)


if __name__ == "__main__":
    main()
