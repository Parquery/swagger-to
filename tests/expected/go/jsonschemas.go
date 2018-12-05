package uber

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

var jsonSchemaProfileText = `{
  "title": "Profile",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "definitions": {
    "Profile": {
      "type": "object",
      "properties": {
        "first_name": {
          "type": "string",
          "description": "First name of the Uber user."
        },
        "last_name": {
          "type": "string",
          "description": "Last name of the Uber user."
        },
        "email": {
          "type": "string",
          "description": "Email address of the Uber user"
        },
        "picture": {
          "type": "string",
          "description": "Image URL of the Uber user."
        },
        "promo_code": {
          "type": "string",
          "description": "Promo code of the Uber user."
        }
      },
      "required": [
        "last_name",
        "email",
        "picture"
      ]
    }
  },
  "$ref": "#/definitions/Profile"
}`

var jsonSchemaProductText = `{
  "title": "Product",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "product_id": {
      "type": "string",
      "description": "Unique identifier representing a specific product for a given latitude & longitude.\nFor example, uberX in San Francisco will have a different product_id than uberX in Los Angeles."
    },
    "desc": {
      "type": "string",
      "description": "Description of product."
    },
    "display_name": {
      "type": "string",
      "description": "Display name of product."
    },
    "capacity": {
      "type": "integer",
      "format": "int32",
      "description": "Capacity of product. For example, 4 people."
    },
    "image": {
      "type": "string",
      "description": "Image URL representing the product."
    }
  },
  "required": [
    "product_id",
    "desc",
    "display_name",
    "capacity",
    "image"
  ]
}`

var jsonSchemaProductListText = `{
  "title": "ProductList",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "definitions": {
    "Product": {
      "type": "object",
      "properties": {
        "product_id": {
          "type": "string",
          "description": "Unique identifier representing a specific product for a given latitude & longitude.\nFor example, uberX in San Francisco will have a different product_id than uberX in Los Angeles."
        },
        "desc": {
          "type": "string",
          "description": "Description of product."
        },
        "display_name": {
          "type": "string",
          "description": "Display name of product."
        },
        "capacity": {
          "type": "integer",
          "format": "int32",
          "description": "Capacity of product. For example, 4 people."
        },
        "image": {
          "type": "string",
          "description": "Image URL representing the product."
        }
      },
      "required": [
        "product_id",
        "desc",
        "display_name",
        "capacity",
        "image"
      ]
    }
  },
  "type": "object",
  "properties": {
    "products": {
      "description": "Contains the list of products",
      "type": "array",
      "items": {
        "$ref": "#/definitions/Product"
      }
    }
  },
  "required": [
    "products"
  ]
}`

var jsonSchemaProductMapText = `{
  "title": "ProductMap",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "definitions": {
    "Product": {
      "type": "object",
      "properties": {
        "product_id": {
          "type": "string",
          "description": "Unique identifier representing a specific product for a given latitude & longitude.\nFor example, uberX in San Francisco will have a different product_id than uberX in Los Angeles."
        },
        "desc": {
          "type": "string",
          "description": "Description of product."
        },
        "display_name": {
          "type": "string",
          "description": "Display name of product."
        },
        "capacity": {
          "type": "integer",
          "format": "int32",
          "description": "Capacity of product. For example, 4 people."
        },
        "image": {
          "type": "string",
          "description": "Image URL representing the product."
        }
      },
      "required": [
        "product_id",
        "desc",
        "display_name",
        "capacity",
        "image"
      ]
    }
  },
  "type": "object",
  "additionalProperties": {
    "$ref": "#/definitions/Product"
  }
}`

var jsonSchemaPriceEstimateText = `{
  "title": "PriceEstimate",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "product_id": {
      "type": "string",
      "description": "Unique identifier representing a specific product for a given latitude & longitude. For example,\nuberX in San Francisco will have a different product_id than uberX in Los Angeles"
    },
    "currency_code": {
      "type": "string",
      "description": "[ISO 4217](http://en.wikipedia.org/wiki/ISO_4217) currency code."
    },
    "display_name": {
      "type": "string",
      "description": "Display name of product."
    },
    "estimate": {
      "type": "string",
      "description": "Formatted string of estimate in local currency of the start location.\nEstimate could be a range, a single number (flat rate) or \"Metered\" for TAXI."
    },
    "low_estimate": {
      "type": "number",
      "format": "double",
      "description": "Lower bound of the estimated price."
    },
    "high_estimate": {
      "type": "number",
      "format": "double",
      "description": "Upper bound of the estimated price."
    },
    "surge_multiplier": {
      "type": "number",
      "format": "double",
      "description": "Expected surge multiplier. Surge is active if surge_multiplier is greater than 1.\nPrice estimate already factors in the surge multiplier."
    }
  },
  "required": [
    "product_id",
    "currency_code",
    "display_name",
    "estimate"
  ]
}`

var jsonSchemaPriceEstimateArrayText = `{
  "title": "PriceEstimateArray",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "definitions": {
    "Product": {
      "type": "object",
      "properties": {
        "product_id": {
          "type": "string",
          "description": "Unique identifier representing a specific product for a given latitude & longitude.\nFor example, uberX in San Francisco will have a different product_id than uberX in Los Angeles."
        },
        "desc": {
          "type": "string",
          "description": "Description of product."
        },
        "display_name": {
          "type": "string",
          "description": "Display name of product."
        },
        "capacity": {
          "type": "integer",
          "format": "int32",
          "description": "Capacity of product. For example, 4 people."
        },
        "image": {
          "type": "string",
          "description": "Image URL representing the product."
        }
      },
      "required": [
        "product_id",
        "desc",
        "display_name",
        "capacity",
        "image"
      ]
    }
  },
  "type": "array",
  "items": {
    "$ref": "#/definitions/Product"
  }
}`

var jsonSchemaActivityText = `{
  "title": "Activity",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "uuid": {
      "type": "string",
      "description": "Unique identifier for the activity"
    }
  },
  "required": [
    "uuid"
  ]
}`

var jsonSchemaActivitiesText = `{
  "title": "Activities",
  "$schema": "http://json-schema.org/draft-04/schema#",
  "definitions": {
    "Activity": {
      "type": "object",
      "properties": {
        "uuid": {
          "type": "string",
          "description": "Unique identifier for the activity"
        }
      },
      "required": [
        "uuid"
      ]
    }
  },
  "type": "object",
  "properties": {
    "offset": {
      "type": "integer",
      "format": "int32",
      "description": "Position in pagination."
    },
    "limit": {
      "type": "integer",
      "format": "int32",
      "description": "Number of items to retrieve (100 max)."
    },
    "count": {
      "type": "integer",
      "format": "int64",
      "description": "Total number of items available."
    },
    "history": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Activity"
      }
    }
  },
  "required": [
    "offset",
    "limit",
    "count",
    "history"
  ]
}`

var jsonSchemaProfile = mustNewJSONSchema(
	jsonSchemaProfileText,
	"Profile")

var jsonSchemaProduct = mustNewJSONSchema(
	jsonSchemaProductText,
	"Product")

var jsonSchemaProductList = mustNewJSONSchema(
	jsonSchemaProductListText,
	"ProductList")

var jsonSchemaProductMap = mustNewJSONSchema(
	jsonSchemaProductMapText,
	"ProductMap")

var jsonSchemaPriceEstimate = mustNewJSONSchema(
	jsonSchemaPriceEstimateText,
	"PriceEstimate")

var jsonSchemaPriceEstimateArray = mustNewJSONSchema(
	jsonSchemaPriceEstimateArrayText,
	"PriceEstimateArray")

var jsonSchemaActivity = mustNewJSONSchema(
	jsonSchemaActivityText,
	"Activity")

var jsonSchemaActivities = mustNewJSONSchema(
	jsonSchemaActivitiesText,
	"Activities")

// ValidateAgainstProfileSchema validates a message coming from the client against Profile schema.
func ValidateAgainstProfileSchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaProfile.Validate(loader)
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

// ValidateAgainstProductSchema validates a message coming from the client against Product schema.
func ValidateAgainstProductSchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaProduct.Validate(loader)
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

// ValidateAgainstProductListSchema validates a message coming from the client against ProductList schema.
func ValidateAgainstProductListSchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaProductList.Validate(loader)
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

// ValidateAgainstProductMapSchema validates a message coming from the client against ProductMap schema.
func ValidateAgainstProductMapSchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaProductMap.Validate(loader)
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

// ValidateAgainstPriceEstimateSchema validates a message coming from the client against PriceEstimate schema.
func ValidateAgainstPriceEstimateSchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaPriceEstimate.Validate(loader)
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

// ValidateAgainstPriceEstimateArraySchema validates a message coming from the client against PriceEstimateArray schema.
func ValidateAgainstPriceEstimateArraySchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaPriceEstimateArray.Validate(loader)
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

// ValidateAgainstActivitySchema validates a message coming from the client against Activity schema.
func ValidateAgainstActivitySchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaActivity.Validate(loader)
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

// ValidateAgainstActivitiesSchema validates a message coming from the client against Activities schema.
func ValidateAgainstActivitiesSchema(bb []byte) error {
	loader := gojsonschema.NewStringLoader(string(bb))
	result, err := jsonSchemaActivities.Validate(loader)
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
