package test

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import (
	"github.com/gorilla/mux"
	"net/http"
	"strconv"
)

// SetupRouter sets up a router. If you don't use any middleware, you are good to go.
// Otherwise, you need to maually re-implement this function with your middlewares.
func SetupRouter(h Handler) *mux.Router {
	r := mux.NewRouter()

	r.HandleFunc(`/products`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapTestMe(h, w, r)
		}).Methods("get")

	return r
}

// WrapTestMe wraps the path `/products` with the method "get".
//
// Path description:
// is a test endpoint.
func WrapTestMe(h Handler, w http.ResponseWriter, r *http.Request) {
	var aSomeParameter string
	var aSomeOptional *string
	var aXSomeCustomParameter int64

	hdr := r.Header

	if _, ok := hdr["Some-parameter"]; !ok {
		http.Error(w, "Parameter 'Some-parameter' expected in header", http.StatusBadRequest)
		return
	}
	aSomeParameter = hdr.Get("Some-parameter")

	if _, ok := hdr["Some-optional"]; ok {
		val := hdr.Get("Some-optional")
		aSomeOptional = &val
	}

	if _, ok := hdr["X-Some-Custom-Parameter"]; !ok {
		http.Error(w, "Parameter 'X-Some-Custom-Parameter' expected in header", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseInt(hdr.Get("X-Some-Custom-Parameter"), 10, 64)
		if err != nil {
			http.Error(w, "Parameter 'X-Some-Custom-Parameter': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := int64(parsed)
		aXSomeCustomParameter = converted
	}

	h.TestMe(w,
		r,
		aSomeParameter,
		aSomeOptional,
		aXSomeCustomParameter)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
