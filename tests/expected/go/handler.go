package uber

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import "net/http"

// Handler defines an interface to handling the routes.
type Handler interface {
	// Products handles the path `/products` with the method "get".
	//
	// Path description:
	// The Products endpoint returns information about the Uber products offered at a given location.
	Products(w http.ResponseWriter,
		r *http.Request,
		latitude float64,
		longitude float64)

	// EstimatesPrice handles the path `/estimates/price/{start_latitude}/{start_longitude}/{end_latitude}/{end_longitude}` with the method "get".
	//
	// Path description:
	// The Price Estimates endpoint returns an estimated price range for each product offered at a given
	// location. The price estimate is provided as a formatted string with the full price range and the localized
	// currency symbol.
	EstimatesPrice(w http.ResponseWriter,
		r *http.Request,
		startLatitude float64,
		startLongitude float64,
		endLatitude float64,
		endLongitude float64,
		maxLines *int32)

	// EstimatesTime handles the path `/estimates/time` with the method "get".
	//
	// Path description:
	// The Time Estimates endpoint returns ETAs for all products.
	EstimatesTime(w http.ResponseWriter,
		r *http.Request,
		startLatitude float64,
		startLongitude float64,
		customerUuid *string,
		productID *string)

	// UpdateMe handles the path `/me` with the method "patch".
	//
	// Path description:
	// Update an User Profile.
	UpdateMe(w http.ResponseWriter,
		r *http.Request,
		updateUser Profile)

	// UploadInfos handles the path `/upload_infos` with the method "patch".
	//
	// Path description:
	// Upload information about an User.
	UploadInfos(w http.ResponseWriter,
		r *http.Request)

	// History handles the path `/history` with the method "get".
	//
	// Path description:
	// The User Activity endpoint returns data about a user's lifetime activity with Uber. The response will
	// include pickup locations and times, dropoff locations and times, the distance of past requests, and
	// information about which products were requested.
	History(w http.ResponseWriter,
		r *http.Request,
		offset *int32,
		limit *int32)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
