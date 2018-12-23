package test_server

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import "net/http"

// Handler defines an interface to handling the routes.
type Handler interface {
	// Upload handles the path `/upload` with the method "put".
	Upload(w http.ResponseWriter,
		r *http.Request)

	// Static handles the path `/{path:.+}` with the method "get".
	//
	// Path description:
	// serves a static file that matches the path.
	Static(w http.ResponseWriter,
		r *http.Request,
		path string)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
