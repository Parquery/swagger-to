3.0.1
=====
* Added new line before ``:return:`` in swagger-to-py-client.
* swagger-to-py-client capitalizes the first letter of class and request function docstrings, respectively.
* Stripped trailing white spaces in swagger-to-go-server and py-client templates.
* Added ``date-time`` test case for swagger-to-go-server and py-client.
* Fixed contract violation in go server due to one-line imports ending in a superfluous new line.

3.0.0
=====
The major change is:

* Made all functions protected in the modules responsible for code generation.

  This impacts only the users which used swagger-to as a library. This change does not affect users which use
  swagger-to only as CLI.

The minor changes are:

* Rewritten go-server and py-client generation with jinja2 template engine.

  The generated code is semantically equal to the previous version, but a bit more readable and easier to diff
  since we enforce now the line width of 100 columns and split argument lists into multiple lines.
* swagger-to-py-client includes a response description in the docstring of the request function.
* Refactored tests into a hierarchy of test case directories
* Added test cases with files, empty objects and objects with optional fields to swagger-to-py-client and go-server.

2.4.0
=====
* swagger-to-elm-client ignores formData parameters gracefully
* Added `no_samples` flag to swagger-to-elm-client and swagger-to-go-server to
  avoid generating sample files.

2.3.0
=====
* swagger-to-elm-client allows non-JSON endpoints
* swagger-to-elm-client uses standard library for encoding URLs

2.2.4
=====
* swagger-to-py-client sets the correct type for the optional properties to make the generated code
  compliant with mypy 0.630

2.2.3
=====
* Fixed swagger-to-py-client to include suffixes in the names of intermediate representations of the
  optional properties in ``X_from_obj``

2.2.2
=====
* swagger-to-py-client suffixes values parsed from an object to avoid conflicts with ``path`` field
* swagger-to-py-client adds type assertions to make the generated code compliant with mypy 0.630

2.2.1
=====
* Fixed that anonymous types of body parameters are named in intermediate representation.

2.2.0
=====
* Added options to style checks to include line numbers of failed checks and verbose error messages.
* Added tests for comparing the output of all generation scripts against expected values.

2.1.0
=====
* Added a script to generate Elm client code.
* Added a script to check Swagger files for style (descriptions, definition names, property names).

2.0.2
=====
* Moved to github.com.
* Added py.typed to comply with mypy.

2.0.1
=====
* Swagger-to-python-client generates the code conform to PEP 257.

2.0.0
=====
* Added swagger-to-elm-client.
* Renamed x-pqry-no-go to x-swagger-to-skip.
* Fixed error messages in Python client copy/pasted from Typsecript client.

1.1.1
=====
* Default parameters values explicitly not supported.

1.1.0
=====
* Swagger-to-go-server does not generate code to extract the parameters from form data.

1.0.2
=====
* Added more related projects to the Readme.

1.0.1
=====
* Changed the copyright to Parquery from Marko Ristin (mistake in the initial version).
* Added versioning description to Readme.

1.0.0
=====
* Initial version.

