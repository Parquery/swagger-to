Swagger-to
==========

Swagger-to generates server and client code from Swagger (OpenAPI 2.0) specification; written in Python 3.

We wanted a code generator that is 1) easy to write, maintain and extend and that 2) produces readable code.

To achieve this, we wrote the tool in Python which we found to be far superior for code generation compared with other
languages such as Go and Java. Since the original Swagger specification can become quite complex, we introduce an
intermediate representation layer after parsing the specification and before generating the code. This layer allowed us
to substantially simplify the generation code since it reduced the impedance mismatch by operating on abstract
constructs (such as Maps) instead of directly referring to "raw" Swagger constructs (such as additional properties of
an object).

The underlying language (Python), readable generated code and the intermediate representation layer are the two main
differentiators to other similar code generation projects.

Supported languages:

====================    ======  ======
Language                Client  Server
====================    ======  ======
Elm                     x
Go                              x
Python                  x
Typescript + Angular    x
====================    ======  ======

Missing Features
----------------
Due to the lack of time, we can not cover all of the Swagger specification. The current generators work well for all of
our simple and not-so-simple use cases. We believe they can also cover most of the other people's needs as well.

Here is a non-comprehensive list.

* **definitions**. We don't support anonymous objects in the definitions. Please define all objects as top level
  definitions.

* **parameters**. Most generators cover only query, body and path parameters. We do not support default values for the
  parameters due to impedance mismatch between JSON and the target languages.

* **responses**. Responses from the server are not validated due to the complexity and run-time overhead.

Related Projects
================
We list here some of the related projects and comment why they did not satisfy our requirements.

* https://github.com/go-swagger/go-swagger produces code which looked a bit too clumsy for us.
* https://github.com/swagger-api/swagger-codegen written in Java and hence hard for us to extend and customize.
* https://grpc.io/ gRPC is great when remote procedure calls are all you need. However, it requires you to use HTTP 2,
  and we found it hard to integrate with widely-used browsers as clients.

  Additionally, streaming files was not directly supported (see https://github.com/grpc/grpc-go/issues/414).
* https://github.com/grpc-ecosystem/grpc-gateway provides a JSON gateway to gRPC. We found that it added an additional
  layer of complexity (especially when the number of client/server pairs grow), and preferred to have a simple solution
  with a single code generation tool.
* https://github.com/twitchtv/twirp a (better?) alternative if you only want to generate remote procedure calls based on
  JSON using protocol buffers to specify the API. It forces you to stick to its representation, though, and does not
  allow you to use an arbitrary Swagger specification. This is problematic when the interface is imposed on you from
  outside (*e.g.*, by customers).

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

Elm Client
----------
To generate an Elm client from a Swagger specification at ``/some/path/swagger.yaml``, invoke:

.. code-block:: bash

    swagger_to_elm_client.py \
        --swagger_path /some/path/swagger.yaml \
        --outdir /some/elm/path/src/your-client-directory

The generated code will have the following structure in ``/some/elm/path/src/your-client-directory``:

===========================  ========================================================================================
File                         Description
===========================  ========================================================================================
``Client.elm``               Elm Client, containing Models, Encoders, Decoders and Http Requests.
``elm-package.sample.json``  The Elm JSON Package containing the libraries used in Client.elm.
===========================  ========================================================================================

Three non-standard libraries are used in the Client:

* "NoRedInk/elm-decode-pipeline" is used to decode JSON objects in a more scalable way than the one supported by the
  elm-lang libraries;
* "elm-community/json-extra" is needed to encode Dict variables;
* "Bogdanp/elm-querystring" is used to deal with queries in URLs;


We use Elm's built-in Int type to represent both 32 and 64-bit integers. Please be careful: Elm depends on JavaScript
which uses solely double-precision floats both for integers and for floating-point numbers, which can lead to
unexpected truncation.

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

Pecularities
~~~~~~~~~~~~
* **parameters**. We decided to generate the code to extract the parameters only from queries, bodies and paths.

  It seemed difficult to automatically generate the code to extract form data arguments which would cover all the edge
  cases (such as files and duplicate entries). We still generate the handler function, but leave it to the programmer
  to extract these arguments manually from the request.

  Due to lack of time, we did not implement header and cookie parameters. Contributions for these features are highly
  welcome!

* **response**. The auto-generated code does not check that the response conforms to the specification. We found such
  checks to be unnecessarily constraining and almost impossible to implement for all the use cases.


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

We use Typescript's built-in number type to represent both 32 and 64-bit integers. Please be careful: Typescript
depends on JavaScript which uses solely double-precision floats both for integers and for floating-point numbers,
which can lead to unexpected truncation.


Style Check
-----------
We found it important to have a uniform documentation style across all the Swagger specifications in an organization.
To that end, swagger_to includes an utility to automatically check the style such as casing of the definition names,
property names, descriptions and verb moods (present tense instead of imperative).To check the compliance of a Swagger
specification at ``/some/path/swagger.yaml`` to the Swagger style guides, invoke:

.. code-block:: bash

    swagger_style.py \
        --swagger_path /some/path/swagger.yaml


The following checks are performed:

* The Swagger name is in camel case, its description capitalized, and the base path starts with a slash.
* Top level type definitions are in capitalized camel case, and properties are in snake case.
* Endpoint paths, operation_id and parameter names are in camel case.
* All descriptions:
    * start with a present tense verb, whose first letter is lower case;
    * have no leading or trailing whitespaces, tabs or new lines;
    * contain either one line, or three or more, in which case the second is empty;
    * end with a period.
* Endpoint paths start with a slash, and the responses contain "200" and "default".

The script call returns 0 in case of no violations found, 1 in case of failed checks or 2 in case of illegal usage.


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