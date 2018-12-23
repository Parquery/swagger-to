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
    "Capacity": {
      "type": "integer",
      "format": "int32",
      "description": "is an identifiable primitive definition."
    },
    "TestObject": {
      "description": "is a test object.",
      "type": "object",
      "properties": {
        "product_id": {
          "type": "string",
          "description": "is a test string property."
        },
        "capacity": {
          "$ref": "#/definitions/Capacity"
        }
      }
    }
  },
  "$ref": "#/definitions/TestObject"
}`

var jsonSchemaCapacityText = `{
  "title": "Capacity",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "integer",
  "format": "int32",
  "description": "is an identifiable primitive definition."
}`

var jsonSchemaTestObject = mustNewJSONSchema(
	jsonSchemaTestObjectText,
	"TestObject")

var jsonSchemaCapacity = mustNewJSONSchema(
	jsonSchemaCapacityText,
	"Capacity")

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

// ValidateAgainstCapacitySchema validates a message coming from the client against Capacity schema.
func ValidateAgainstCapacitySchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaCapacity.Validate(loader)
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
