#!/usr/bin/env python3
"""
Reads a correct swagger file and checks whether it conforms to a style guide.
"""
import argparse
import pathlib

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
    args = parser.parse_args()

    assert isinstance(args.swagger_path, str)

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
        print("Style checks failed: \n{}".format("\n".join(result)))
        return 1

    print("Style checks succeeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
