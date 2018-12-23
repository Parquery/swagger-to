package test

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import (
	"encoding/json"
	"github.com/gorilla/mux"
	"io/ioutil"
	"net/http"
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

// WrapTestMe wraps the path `/products` with the method "get"
//
// Path description:
// is a test endpoint.
func WrapTestMe(h Handler, w http.ResponseWriter, r *http.Request) {
	var aTestObject TestObject

	if r.Body != nil {
		{
			var err error
			r.Body = http.MaxBytesReader(w, r.Body, 1024*1024)
			body, err := ioutil.ReadAll(r.Body)
			if err != nil {
				http.Error(w, "Body unreadable: "+err.Error(), http.StatusBadRequest)
				return
			}

			err = ValidateAgainstTestObjectSchema(body)
			if err != nil {
				http.Error(w, "Failed to validate against schema: "+err.Error(), http.StatusBadRequest)
				return
			}

			err = json.Unmarshal(body, &aTestObject)
			if err != nil {
				http.Error(w, "Error JSON-decoding body parameter 'test_object': "+err.Error(),
					http.StatusBadRequest)
				return
			}
		}
	}

	h.TestMe(w,
		r,
		aTestObject)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
