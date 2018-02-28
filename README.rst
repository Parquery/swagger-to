Swagger-to
==========

Generates server and client code from Swagger (OpenAPI 2.0) specification; written in Python 3.

The following tools could not satisfy our requirements:

* https://github.com/go-swagger/go-swagger produces code which looks a bit too clumsy for us,
* https://github.com/swagger-api/swagger-codegen is written in Java and hence hard for us to extend and customize.

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