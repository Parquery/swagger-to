#!/usr/bin/env python3
"""
Reads a correct swagger file and checks whether it conforms to a style guide.
"""
import argparse
import pathlib
from typing import List

import sys

import swagger_to.intermediate
import swagger_to.style
import swagger_to.swagger


def main() -> int:
    """"
    Main routine
    """
    parser = argparse.ArgumentParser("Reads a correct swagger file and checks that it conforms to the style guide.")
    parser.add_argument("--swagger_path", help="path to the swagger file", required=True)
    parser.add_argument("--verbose", help="if set, prints as much information as possible.", action="store_true")
    parser.add_argument(
        "--with_line_number",
        help="if set, prints the errors with the corresponding file name and line number.",
        action="store_true")
    args = parser.parse_args()

    assert isinstance(args.swagger_path, str)
    assert isinstance(args.verbose, bool)
    assert isinstance(args.with_line_number, bool)

    swagger_path = pathlib.Path(args.swagger_path)

    if not swagger_path.exists():
        print("File not found error: Swagger file does not exist: {}".format(swagger_path))
        return 2

    swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
    if errs:
        print("Value error: Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))
        return 2

    intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
    intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

    endpoints = swagger_to.intermediate.to_endpoints(
        swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

    result = swagger_to.style.perform(swagger=swagger, typedefs=intermediate_typedefs, endpoints=endpoints)

    if result:
        complaints = '\n'.join(
            format_complaints(
                complaints=result,
                swagger_path=str(swagger_path),
                verbose=args.verbose,
                with_line_number=args.with_line_number))

        print("Style checks failed: \n{}".format(complaints))
        return 1

    print("Style checks succeeded.")
    return 0


def format_complaints(complaints: List[swagger_to.style.Complaint], swagger_path: str, verbose: bool,
                      with_line_number: bool) -> List[str]:
    """
    Converts a list of complaints into a well-formatted list of error messages.

    :param complaints:
    :param swagger_path:
    :param verbose:
    :param with_line_number:
    :return:
    """
    if with_line_number:
        complaints.sort(key=lambda complaint: complaint.line)

    complaints_str = []  # type: List[str]
    for complaint in complaints:
        complaint_str = ''
        if with_line_number:
            complaint_str += "{}:{} ".format(swagger_path, complaint.line)
        else:
            complaint_str += "{}: ".format(complaint.where)

        complaint_str += "{} ".format(complaint.message)

        if verbose:
            complaint_str += "\"{}\"".format(complaint.what.replace('\n', ' '))

        complaints_str.append(complaint_str)

    return complaints_str


if __name__ == "__main__":
    sys.exit(main())
