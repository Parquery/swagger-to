#!/usr/bin/env python3
"""
Reads a correct swagger file and produces Go code
"""
import argparse
import os
import sys

import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.swagger


def main() -> None:
    """"
    Main routine
    """
    parser = argparse.ArgumentParser("Reads a correct swagger file and produces Go code")
    parser.add_argument("--swagger_path", help="path to the swagger file", required=True)
    parser.add_argument("--outdir", help="path to the output directory", required=True)
    parser.add_argument("--no_samples", help="if set, do not generate sample files", action="store_true")
    parser.add_argument("--force", help="overwrite existing files", action="store_true")
    args = parser.parse_args()

    assert isinstance(args.force, bool)
    assert isinstance(args.no_samples, bool)
    assert isinstance(args.outdir, str)
    assert isinstance(args.swagger_path, str)

    if not os.path.exists(args.swagger_path):
        print("Swagger file does not exist: {}".format(args.swagger_path), file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    if not args.force:
        for fname in ['main.go', 'handlers.go', 'types.go', 'routes.go', 'jsonschemas.go']:
            pth = os.path.join(args.outdir, fname)
            if os.path.exists(pth):
                print("File exists, but --force was not specified: {!r}".format(pth))
                sys.exit(1)

    swagger, errs = swagger_to.swagger.parse_yaml_file(path=args.swagger_path)
    if errs:
        raise AssertionError("Errors in {}:\n{}".format(args.swagger_path, "\n".join(errs)))

    intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
    intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

    endpoints = swagger_to.intermediate.to_endpoints(
        swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

    go_typedefs = swagger_to.go_server.to_typedefs(intermediate_typedefs=intermediate_typedefs)
    go_routes = swagger_to.go_server.to_routes(endpoints=endpoints, typedefs=go_typedefs)

    package = swagger.name

    pth = os.path.join(args.outdir, 'types.go')
    with open(pth, 'wt') as fid:
        swagger_to.go_server.write_types_go(package=package, typedefs=go_typedefs, fid=fid)

    pth = os.path.join(args.outdir, 'routes.go')
    with open(pth, 'wt') as fid:
        swagger_to.go_server.write_routes_go(package=package, routes=go_routes, fid=fid)

    pth = os.path.join(args.outdir, 'handler.go')
    with open(pth, 'wt') as fid:
        swagger_to.go_server.write_handler_go(package=package, routes=go_routes, fid=fid)

    if not args.no_samples:
        pth = os.path.join(args.outdir, 'handler_impl.go.sample')
        with open(pth, 'wt') as fid:
            swagger_to.go_server.write_handler_impl_go(package=package, routes=go_routes, fid=fid)

    pth = os.path.join(args.outdir, 'jsonschemas.go')
    with open(pth, 'wt') as fid:
        swagger_to.go_server.write_json_schemas_go(package=package, routes=go_routes, typedefs=go_typedefs, fid=fid)

    print("Generated go server code in: {}".format(args.outdir))


if __name__ == "__main__":
    main()
