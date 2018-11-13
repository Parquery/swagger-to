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

