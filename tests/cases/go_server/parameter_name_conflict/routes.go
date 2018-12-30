package test

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import (
	"github.com/gorilla/mux"
	"net/http"
)

// SetupRouter sets up a router. If you don't use any middleware, you are good to go.
// Otherwise, you need to maually re-implement this function with your middlewares.
func SetupRouter(h Handler) *mux.Router {
	r := mux.NewRouter()

	r.HandleFunc(`/products/{some_parameter}`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapTestMe(h, w, r)
		}).Methods("get")

	return r
}

// WrapTestMe wraps the path `/products/{some_parameter}` with the method "get"
//
// Path description:
// is a test endpoint.
func WrapTestMe(h Handler, w http.ResponseWriter, r *http.Request) {
	var aQuerySomeParameter string
	var aPathSomeParameter string

	q := r.URL.Query()

	if _, ok := q["some_parameter"]; !ok {
		http.Error(w, "Parameter 'some_parameter' expected in query", http.StatusBadRequest)
		return
	}
	aQuerySomeParameter = q.Get("some_parameter")

	vars := mux.Vars(r)

	if _, ok := vars["some_parameter"]; !ok {
		http.Error(w, "Parameter 'some_parameter' expected in path", http.StatusBadRequest)
		return
	}
	aPathSomeParameter = vars["some_parameter"]

	h.TestMe(w,
		r,
		aQuerySomeParameter,
		aPathSomeParameter)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
