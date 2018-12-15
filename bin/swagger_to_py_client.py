#!/usr/bin/env python3
"""Read a correct swagger file and produce Python client code."""
import argparse
import os

import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.py_client
import swagger_to.swagger


def main() -> None:
    """Execute the main routine."""
    parser = argparse.ArgumentParser("Reads a correct swagger file and produces python client code")
    parser.add_argument("--swagger_path", help="path to the swagger file", required=True)
    parser.add_argument("--outpath", help="path to the output file", required=True)
    parser.add_argument("--force", help="overwrite existing files", action="store_true")
    args = parser.parse_args()

    swagger_path = str(args.swagger_path)
    out_path = str(args.outpath)
    force = bool(args.force)

    if not os.path.exists(args.swagger_path):
        raise FileNotFoundError("Swagger file does not exist: {}".format(swagger_path))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if not force and os.path.exists(out_path):
        raise FileExistsError("Output path already exists and --force was not specified: {}".format(out_path))

    swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
    if errs:
        raise AssertionError("Errors in {}:\n{}".format(swagger_path, "\n".join(errs)))

    intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
    intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

    endpoints = swagger_to.intermediate.to_endpoints(
        swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

    py_typedefs = swagger_to.py_client.to_typedefs(intermediate_typedefs=intermediate_typedefs)

    if 'RemoteCaller' in py_typedefs:
        raise ValueError("A definition was specified in the swagger with the name 'RemoteCaller', "
                         "but it's reserved for the Python client class.")

    py_requests = swagger_to.py_client.to_requests(endpoints=endpoints, typedefs=py_typedefs)

    with open(out_path, 'wt') as fid:
        swagger_to.py_client.write_client_py(
            service_name=swagger.name, typedefs=py_typedefs, requests=py_requests, fid=fid)

    print("Generated python client code in: {}".format(out_path))


if __name__ == "__main__":
    main()
