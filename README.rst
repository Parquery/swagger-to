Swagger-to
==========

Generates server and client code from Swagger (OpenAPI 2.0) specification; written in Python 3.

The following tools could not satisfy our requirements:

* https://github.com/go-swagger/go-swagger produces code which looks a bit too clumsy for us,
* https://github.com/swagger-api/swagger-codegen is written in Java and hence hard for us to extend and customize.

Due to the lack of time, we can not cover all of the Swagger specification (please see the source code for the details
or write us a message), but the current generators work well for all of our simple and not-so-simple use cases. We
believe they can also cover most of the other people's needs as well.

Installation
============

* Create a virtual environment:

.. code-block:: bash

    python3 -m venv venv3

* Activate it:

.. code-block:: bash

    source venv3/bin/activate

* Install swagger_to with pip:

.. code-block:: bash

    pip3 install swagger_to

Usage
=====
To generate code, you need to invoke one of the ``swagger_to_*.py`` scripts. If the generated code exists, you need to
specify ``--force`` command-line argument in order to overwrite the existing files.

Go Server
---------
To generate a Go server from a Swagger specification at ``/some/path/swagger.yaml``, invoke:

.. code-block:: bash

    swagger_to_go_server.py \
        --swagger_path /some/path/swagger.yaml \
        --outdir /some/go/path/src/your-server-package

The generated code will have the following structure in ``/some/go/path/src/your-server-package``:

==========================  ========================================================================================
File                        Description
==========================  ========================================================================================
``types.go``                Go type definitions
``jsonschemas.go``          JSON schemas used to validate the input (using https://github.com/xeipuuv/gojsonschema)
``routes.go``               Router specification
``handler.go``              Handler interface
``handler_impl.sample.go``  Empty implementation of the handler
==========================  ========================================================================================

All the types defined in the Swagger are translated to ``types.go``. The routing and validation code around
the endpoints is generated in ``jsonschemas.go`` and ``routes.go``.

The handler interface is given in ``handler.go``. You need to implement the handler logic yourself. You can use
``handler_impl.sample.go`` as a starting point. We usually just copy/paste it to ``handler_impl.go`` and ignore
``handler_impl.sample.go`` in our repositories (*e.g.*, by adding it to ``.gitignore``).

In face of Swagger (*i.e.* API) changes, our workflow includes regenerating the code and using a diff tool
like ``meld`` to sync the "old" ``handler_impl.go`` with the new ``handler_impl.sample.go``.

Python Client
-------------
To generate a Python 3 client from a Swagger specification at ``/some/path/swagger.yaml``, invoke:

.. code-block:: bash

    swagger_to_py_client.py \
        --swagger_path /some/path/swagger.yaml \
        --outpath /some/py/path/your_client_module.py

The generated client uses ``requests`` library.

Since input checks need to be performed by the server anyhow, we decided not to keep the code generator simple and
more maintainable by including only the rudimentary type checks on the inputs. Hence all the sophisticated checks
such as string patterns or casting of a Python integer to int32 are deliberately excluded. Analogously, we also
do not validate the output coming from the server.

If time ever permits, we would like to include both more fine-grained input and output validation. At the moment,
we did not confront any problems in the development process.


Typescript+Angular Client
-------------------------
To generate a Python client from a Swagger specification at ``/some/path/swagger.yaml``, invoke:

.. code-block:: bash

    swagger_to_ts_angular5_client.py \
        --swagger_path /some/path/swagger.yaml \
        --outpath /some/typescript/path/your_client.ts

The generated client uses Angular ``http`` library. For the same reasons as for Python client, no checks are performed
neither on the input nor on the output.


Development
===========

* Check out the repository.

* In the repository root, create the virtual environment:

.. code-block:: bash

    python3 -m venv venv3

* Activate the virtual environment:

.. code-block:: bash

    source venv3/bin/activate

* Install the development dependencies:

.. code-block:: bash

    pip3 install -e .[dev]

* Run `precommit.py` to execute pre-commit checks locally.

Versioning
==========
We follow `Semantic Versioning <http://semver.org/spec/v1.0.0.html>`_. The version X.Y.Z indicates:

* X is the major version (backward-incompatible),
* Y is the minor version (backward-compatible), and
* Z is the patch version (backward-compatible bug fix).