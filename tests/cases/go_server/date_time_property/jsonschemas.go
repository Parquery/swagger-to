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

var jsonSchemaTestObjectText = `{
  "title": "TestObject",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "definitions": {
    "TestObject": {
      "description": "is a test object.",
      "type": "object",
      "properties": {
        "timestamp": {
          "type": "string",
          "description": "is a test string property.",
          "format": "date-time"
        }
      },
      "required": [
        "timestamp"
      ]
    }
  },
  "$ref": "#/definitions/TestObject"
}`

var jsonSchemaTestObject = mustNewJSONSchema(
	jsonSchemaTestObjectText,
	"TestObject")

// ValidateAgainstTestObjectSchema validates a message coming from the client against TestObject schema.
func ValidateAgainstTestObjectSchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaTestObject.Validate(loader)
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
