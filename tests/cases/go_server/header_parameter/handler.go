package test

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import "net/http"

// Handler defines an interface to handling the routes.
type Handler interface {
	// TestMe handles the path `/products` with the method "get".
	//
	// Path description:
	// is a test endpoint.
	TestMe(w http.ResponseWriter,
		r *http.Request,
		someParameter string,
		someOptional *string,
		xSomeCustomParameter int64)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
