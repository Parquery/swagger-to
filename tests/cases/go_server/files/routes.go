package test_server

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import (
	"github.com/gorilla/mux"
	"net/http"
)

// SetupRouter sets up a router. If you don't use any middleware, you are good to go.
// Otherwise, you need to maually re-implement this function with your middlewares.
func SetupRouter(h Handler) *mux.Router {
	r := mux.NewRouter()

	r.HandleFunc(`/upload`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapUpload(h, w, r)
		}).Methods("put")

	r.HandleFunc(`/{path:.+}`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapStatic(h, w, r)
		}).Methods("get")

	return r
}

// WrapUpload wraps the path `/upload` with the method "put".
func WrapUpload(h Handler, w http.ResponseWriter, r *http.Request) {
	h.Upload(w, r)
}

// WrapStatic wraps the path `/{path:.+}` with the method "get".
//
// Path description:
// serves a static file that matches the path.
func WrapStatic(h Handler, w http.ResponseWriter, r *http.Request) {
	var aPath string

	vars := mux.Vars(r)

	if _, ok := vars["path"]; !ok {
		http.Error(w, "Parameter 'path' expected in path", http.StatusBadRequest)
		return
	}
	aPath = vars["path"]

	h.Static(w,
		r,
		aPath)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
