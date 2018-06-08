#!/usr/bin/env python3
"""
Runs a live test of swagger_to_elm.

Generates the files in a temporary directory and compiles them with the ELM compiler available on your PATH. It also
formats them with elm-format and lints them with elm-analyse,if they are available on your PATH.
"""
import argparse
import contextlib
import os
import pathlib
import shlex
import subprocess
import sys
import tempfile


def main() -> int:
    """
    Main routine
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--swagger_dir",
        help="path to the directory that holds swagger files. Recursively walks this directory and "
        "generates Elm client code for each swagger.yaml or swagger.json.",
        required=True)
    parser.add_argument("--output_dir", help="path to the output directory; if not specified, a temporary directory.")
    args = parser.parse_args()

    swagger_dir = pathlib.Path(args.swagger_dir)

    swagger_pths = list(swagger_dir.glob(pattern="**/swagger.yaml"))
    swagger_pths.extend(swagger_dir.glob(pattern="**/swagger.json"))

    if len(swagger_pths) == 0:
        print("There are no swagger specifications in: {}".format(swagger_dir))
        return 1

    output_dir = pathlib.Path(args.output_dir) if args.output_dir is not None else None

    with contextlib.ExitStack() as exit_stack:
        if output_dir is None:
            tmp_dir = tempfile.TemporaryDirectory()
            exit_stack.push(tmp_dir)
            output_dir = pathlib.Path(tmp_dir.name)

        script_dir = pathlib.Path(os.path.realpath(__file__)).parent

        for swagger_pth in swagger_pths:
            outdir = output_dir / swagger_pth.parent.relative_to(swagger_dir)
            if not outdir.exists():
                pathlib.Path.mkdir(outdir, parents=True)
            # yapf: disable
            cmd = [
                (script_dir.parent / 'bin' / 'swagger_to_elm_client.py').as_posix(),
                '--swagger_path', swagger_pth.as_posix(),
                '--outdir', str(outdir),
                '--force'
            ]
            # yapf: enable

            retcode = subprocess.call(cmd)
            if retcode != 0:
                raise RuntimeError("The command failed: {}".format(' '.join([shlex.quote(part) for part in cmd])))
            if subprocess.call(['which', 'elm']) == 0:
                os.rename(outdir.as_posix() + '/elm-package.sample.json', outdir.as_posix() + '/elm-package.json')

                # subprocess.check_call(['elm', 'make', '--yes'], cwd=str(outdir))
                subprocess.check_call(['elm', 'make', 'Client.elm', '--yes'], cwd=str(outdir))
                if subprocess.call(['which', 'elm-format']) == 0 and subprocess.call(['which', 'elm-analyse']) == 0:
                    subprocess.check_call(['elm', 'format', 'Client.elm', '--yes'], cwd=str(outdir))
                    subprocess.check_call(['elm', 'analyse'], cwd=str(outdir))
                else:
                    print("No linting checks made, since elm-format and elm-analyse could not be found on your PATH.")

                print("Successfully built {}".format(outdir))
            else:
                print("Elm could not be found on your PATH, hence the compilation can not be tested.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
