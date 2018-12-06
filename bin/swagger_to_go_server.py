#!/usr/bin/env python3
"""
Reads a correct swagger file and produces Go code
"""
import argparse
import pathlib
import sys
from typing import cast, TextIO

import swagger_to.go_server
import swagger_to.intermediate
import swagger_to.swagger


def main() -> None:
    """Executes the main routine."""
    # pylint: disable=too-many-locals
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

    force = bool(args.force)
    no_samples = bool(args.no_samples)
    swagger_path = pathlib.Path(args.swagger_path)
    outdir = pathlib.Path(args.outdir)

    if not swagger_path.exists():
        print("Swagger file does not exist: {}".format(swagger_path), file=sys.stderr)
        sys.exit(1)

    outdir.mkdir(parents=True, exist_ok=True)

    if not force:
        for fname in ['main.go', 'handlers.go', 'types.go', 'routes.go', 'jsonschemas.go']:
            pth = outdir / fname
            if pth.exists():
                print("File exists, but --force was not specified: {!r}".format(pth), file=sys.stderr)
                sys.exit(1)

    swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path.as_posix())
    if errs:
        raise AssertionError("Errors in {}:\n{}".format(swagger_path, "\n".join(errs)))

    intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)
    intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

    endpoints = swagger_to.intermediate.to_endpoints(
        swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

    go_typedefs = swagger_to.go_server.to_typedefs(intermediate_typedefs=intermediate_typedefs)
    go_routes = swagger_to.go_server.to_routes(endpoints=endpoints, typedefs=go_typedefs)

    package = swagger.name

    with (outdir / 'types.go').open('wt') as fid:
        swagger_to.go_server.write_types_go(package=package, typedefs=go_typedefs, fid=cast(TextIO, fid))

    with (outdir / 'routes.go').open('wt') as fid:
        swagger_to.go_server.write_routes_go(package=package, routes=go_routes, fid=cast(TextIO, fid))

    with (outdir / 'handler.go').open('wt') as fid:
        swagger_to.go_server.write_handler_go(package=package, routes=go_routes, fid=cast(TextIO, fid))

    if not no_samples:
        with (outdir / 'handler_impl.go.sample').open('wt') as fid:
            swagger_to.go_server.write_handler_impl_go(package=package, routes=go_routes, fid=cast(TextIO, fid))

    with (outdir / 'jsonschemas.go').open('wt') as fid:
        swagger_to.go_server.write_json_schemas_go(
            package=package, routes=go_routes, typedefs=go_typedefs, fid=cast(TextIO, fid))

    print("Generated go server code in: {}".format(outdir))


if __name__ == "__main__":
    main()
