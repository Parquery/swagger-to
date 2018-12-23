package test

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import (
	"errors"
	"fmt"
	"github.com/xeipuuv/gojsonschema"
)

func mustNewJSONSchema(text string, name string) *gojsonschema.Schema {
	loader := gojsonschema.NewStringLoader(text)
	schema, err := gojsonschema.NewSchema(loader)
	if err != nil {
		panic(fmt.Sprintf("failed to load JSON Schema %#v: %s", text, err.Error()))
	}
	return schema
}

var jsonSchemaEmptyObjectText = `{
  "title": "EmptyObject",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "definitions": {
    "EmptyObject": {
      "description": "is an empty object without properties.",
      "type": "object"
    }
  },
  "$ref": "#/definitions/EmptyObject"
}`

var jsonSchemaEmptyObject = mustNewJSONSchema(
	jsonSchemaEmptyObjectText,
	"EmptyObject")

// ValidateAgainstEmptyObjectSchema validates a message coming from the client against EmptyObject schema.
func ValidateAgainstEmptyObjectSchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaEmptyObject.Validate(loader)
	if err != nil {
		return err
	}

	if result.Valid() {
		return nil
	}

	msg := ""
	for i, valErr := range result.Errors() {
		if i > 0 {
			msg += ", "
		}
		msg += valErr.String()
	}
	return errors.New(msg)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
