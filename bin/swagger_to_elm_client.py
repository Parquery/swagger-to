#!/usr/bin/env python3
"""
Reads a correct swagger file and produces Elm client code.
"""
import argparse
import pathlib
import json
from typing import TextIO, cast

import swagger_to.elm_client
import swagger_to.intermediate
import swagger_to.swagger


def main() -> None:
    """"
    Main routine
    """
    # pylint: disable=too-many-locals
    parser = argparse.ArgumentParser("Reads a correct swagger file and produces Elm client code.")
    parser.add_argument("--swagger_path", help="path to the swagger file", required=True)
    parser.add_argument("--outdir", help="path to the output directory", required=True)
    parser.add_argument("--no_samples", help="if set, do not generate sample files", action="store_true")
    parser.add_argument("--force", help="overwrite existing files", action="store_true")
    args = parser.parse_args()

    assert isinstance(args.force, bool)
    assert isinstance(args.no_samples, bool)
    assert isinstance(args.outdir, str)
    assert isinstance(args.swagger_path, str)

    swagger_path = pathlib.Path(args.swagger_path)
    outdir = pathlib.Path(args.outdir)
    force = bool(args.force)

    if not swagger_path.exists():
        raise FileNotFoundError("Swagger file does not exist: {}".format(swagger_path))

    if not outdir.exists():
        pathlib.Path.mkdir(outdir)

    if not force:
        for fname in ['Client.elm', 'elm-package.sample.json']:
            pth = outdir / fname
            if pth.exists():
                raise FileExistsError("File exists, but --force was not specified: {!r}".format(pth))

    swagger, errs = swagger_to.swagger.parse_yaml_file(path=swagger_path)
    if errs:
        raise ValueError("Failed to parse Swagger file {}:\n{}".format(swagger_path, "\n".join(errs)))

    intermediate_typedefs = swagger_to.intermediate.to_typedefs(swagger=swagger)

    intermediate_params = swagger_to.intermediate.to_parameters(swagger=swagger, typedefs=intermediate_typedefs)

    endpoints = swagger_to.intermediate.to_endpoints(
        swagger=swagger, typedefs=intermediate_typedefs, params=intermediate_params)

    elm_typedefs = swagger_to.elm_client.to_typedefs(intermediate_typedefs=intermediate_typedefs)
    elm_requests = swagger_to.elm_client.to_requests(endpoints=endpoints, typedefs=elm_typedefs)

    src_pth = outdir / 'Client.elm'
    with src_pth.open('wt') as fid:
        fid_textio = cast(TextIO, fid)
        swagger_to.elm_client.write_client_elm(typedefs=elm_typedefs, requests=elm_requests, fid=fid_textio)

    if not args.no_samples:
        pkg_pth = outdir / 'elm-package.sample.json'
        elm_package_json = swagger_to.elm_client.elm_package_json()
        with pkg_pth.open('wt') as fid:
            json.dump(elm_package_json, fp=fid, indent=2, sort_keys=False)

    print("Generated Elm client code in: {}".format(outdir))


if __name__ == "__main__":
    main()
