package uber

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

type Product struct {
	// Unique identifier representing a specific product for a given latitude & longitude.
	// For example, uberX in San Francisco will have a different product_id than uberX in Los Angeles.
	ProductID string `json:"product_id"`

	// Description of product.
	Desc string `json:"desc"`

	// Display name of product.
	DisplayName string `json:"display_name"`

	// Capacity of product. For example, 4 people.
	Capacity int32 `json:"capacity"`

	// Image URL representing the product.
	Image string `json:"image"`}

type ProductList struct {
	// Contains the list of products
	Products []Product `json:"products"`}

type ProductMap map[string]Product

type PriceEstimate struct {
	// Unique identifier representing a specific product for a given latitude & longitude. For example,
	// uberX in San Francisco will have a different product_id than uberX in Los Angeles
	ProductID string `json:"product_id"`

	// [ISO 4217](http://en.wikipedia.org/wiki/ISO_4217) currency code.
	CurrencyCode string `json:"currency_code"`

	// Display name of product.
	DisplayName string `json:"display_name"`

	// Formatted string of estimate in local currency of the start location.
	// Estimate could be a range, a single number (flat rate) or "Metered" for TAXI.
	Estimate string `json:"estimate"`

	// Lower bound of the estimated price.
	LowEstimate *float64 `json:"low_estimate,omitempty"`

	// Upper bound of the estimated price.
	HighEstimate *float64 `json:"high_estimate,omitempty"`

	// Expected surge multiplier. Surge is active if surge_multiplier is greater than 1.
	// Price estimate already factors in the surge multiplier.
	SurgeMultiplier *float64 `json:"surge_multiplier,omitempty"`}

type PriceEstimateArray []Product

type Profile struct {
	// First name of the Uber user.
	FirstName *string `json:"first_name,omitempty"`

	// Last name of the Uber user.
	LastName string `json:"last_name"`

	// Email address of the Uber user
	Email string `json:"email"`

	// Image URL of the Uber user.
	Picture string `json:"picture"`

	// Promo code of the Uber user.
	PromoCode *string `json:"promo_code,omitempty"`}

type Activity struct {
	// Unique identifier for the activity
	Uuid string `json:"uuid"`}

type Activities struct {
	// Position in pagination.
	Offset int32 `json:"offset"`

	// Number of items to retrieve (100 max).
	Limit int32 `json:"limit"`

	// Total number of items available.
	Count int64 `json:"count"`

	History []Activity `json:"history"`}
