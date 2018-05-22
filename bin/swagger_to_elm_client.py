#!/usr/bin/env python3
"""
Reads a correct swagger file and produces Elm client code.
"""
import argparse
import pathlib

import swagger_to.elm_client
import swagger_to.intermediate
import swagger_to.swagger


def main() -> None:
    """"
    Main routine
    """
    parser = argparse.ArgumentParser("Reads a correct swagger file and produces Elm client code")
    parser.add_argument("--swagger_path", help="path to the swagger file", required=True)
    parser.add_argument("--outpath", help="path to the generated client file", required=True)
    parser.add_argument("--force", help="overwrite existing file", action="store_true")
    args = parser.parse_args()

    swagger_path = pathlib.Path(args.swagger_path)
    outpath = pathlib.Path(args.outpath)
    force = bool(args.force)

    if not swagger_path.exists():
        raise FileNotFoundError("Swagger file does not exist: {}".format(swagger_path))

    if not force and outpath.exists():
        raise FileExistsError("Output file already exists and --force was not specified: {}".format(outpath))

    swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
    if errs:
        raise ValueError("Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))

    intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
    intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

    endpoints = swagger_to.intermediate.to_endpoints(
        swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

    elm_typedefs = swagger_to.elm_client.to_typedefs(intermediate_typedefs=intermediate_typedefs)
    elm_requests = swagger_to.elm_client.to_requests(endpoints=endpoints, typedefs=elm_typedefs)

    with outpath.open('wt') as fid:
        swagger_to.elm_client.write_client_elm(typedefs=elm_typedefs, requests=elm_requests, fid=fid)

    print("Generated Elm client code in: {}".format(outpath))


if __name__ == "__main__":
    main()
