package uber

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import (
	"encoding/json"
	"github.com/gorilla/mux"
	"io/ioutil"
	"net/http"
	"strconv"
)

// SetupRouter sets up a router. If you don't use any middleware, you are good to go.
// Otherwise, you need to maually re-implement this function with your middlewares.
func SetupRouter(h Handler) *mux.Router {
	r := mux.NewRouter()

	r.HandleFunc(`/products`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapProducts(h, w, r)
		}).Methods("get")

	r.HandleFunc(`/estimates/price/{start_latitude}/{start_longitude}/{end_latitude}/{end_longitude}`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapEstimatesPrice(h, w, r)
		}).Methods("get")

	r.HandleFunc(`/estimates/time`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapEstimatesTime(h, w, r)
		}).Methods("get")

	r.HandleFunc(`/me`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapUpdateMe(h, w, r)
		}).Methods("patch")

	r.HandleFunc(`/upload_infos`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapUploadInfos(h, w, r)
		}).Methods("patch")

	r.HandleFunc(`/history`,
		func(w http.ResponseWriter, r *http.Request) {
			WrapHistory(h, w, r)
		}).Methods("get")

	return r
}

// WrapProducts wraps the path `/products` with the method "get".
//
// Path description:
// The Products endpoint returns information about the Uber products offered at a given location.
func WrapProducts(h Handler, w http.ResponseWriter, r *http.Request) {
	var aLatitude float64
	var aLongitude float64

	q := r.URL.Query()

	if _, ok := q["latitude"]; !ok {
		http.Error(w, "Parameter 'latitude' expected in query", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseFloat(q.Get("latitude"), 64)
		if err != nil {
			http.Error(w, "Parameter 'latitude': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := float64(parsed)
		aLatitude = converted
	}

	if _, ok := q["longitude"]; !ok {
		http.Error(w, "Parameter 'longitude' expected in query", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseFloat(q.Get("longitude"), 64)
		if err != nil {
			http.Error(w, "Parameter 'longitude': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := float64(parsed)
		aLongitude = converted
	}

	h.Products(w,
		r,
		aLatitude,
		aLongitude)
}

// WrapEstimatesPrice wraps the path `/estimates/price/{start_latitude}/{start_longitude}/{end_latitude}/{end_longitude}` with the method "get".
//
// Path description:
// The Price Estimates endpoint returns an estimated price range for each product offered at a given
// location. The price estimate is provided as a formatted string with the full price range and the localized
// currency symbol.
func WrapEstimatesPrice(h Handler, w http.ResponseWriter, r *http.Request) {
	var aStartLatitude float64
	var aStartLongitude float64
	var aEndLatitude float64
	var aEndLongitude float64
	var aMaxLines *int32

	q := r.URL.Query()

	if _, ok := q["max_lines"]; ok {
		{
			parsed, err := strconv.ParseInt(q.Get("max_lines"), 10, 32)
			if err != nil {
				http.Error(w, "Parameter 'max_lines': "+err.Error(), http.StatusBadRequest)
				return
			}
			converted := int32(parsed)
			aMaxLines = &converted
		}
	}

	vars := mux.Vars(r)

	if _, ok := vars["start_latitude"]; !ok {
		http.Error(w, "Parameter 'start_latitude' expected in path", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseFloat(vars["start_latitude"], 64)
		if err != nil {
			http.Error(w, "Parameter 'start_latitude': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := float64(parsed)
		aStartLatitude = converted
	}

	if _, ok := vars["start_longitude"]; !ok {
		http.Error(w, "Parameter 'start_longitude' expected in path", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseFloat(vars["start_longitude"], 64)
		if err != nil {
			http.Error(w, "Parameter 'start_longitude': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := float64(parsed)
		aStartLongitude = converted
	}

	if _, ok := vars["end_latitude"]; !ok {
		http.Error(w, "Parameter 'end_latitude' expected in path", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseFloat(vars["end_latitude"], 64)
		if err != nil {
			http.Error(w, "Parameter 'end_latitude': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := float64(parsed)
		aEndLatitude = converted
	}

	if _, ok := vars["end_longitude"]; !ok {
		http.Error(w, "Parameter 'end_longitude' expected in path", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseFloat(vars["end_longitude"], 64)
		if err != nil {
			http.Error(w, "Parameter 'end_longitude': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := float64(parsed)
		aEndLongitude = converted
	}

	h.EstimatesPrice(w,
		r,
		aStartLatitude,
		aStartLongitude,
		aEndLatitude,
		aEndLongitude,
		aMaxLines)
}

// WrapEstimatesTime wraps the path `/estimates/time` with the method "get".
//
// Path description:
// The Time Estimates endpoint returns ETAs for all products.
func WrapEstimatesTime(h Handler, w http.ResponseWriter, r *http.Request) {
	var aStartLatitude float64
	var aStartLongitude float64
	var aCustomerUuid *string
	var aProductID *string

	q := r.URL.Query()

	if _, ok := q["start_latitude"]; !ok {
		http.Error(w, "Parameter 'start_latitude' expected in query", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseFloat(q.Get("start_latitude"), 64)
		if err != nil {
			http.Error(w, "Parameter 'start_latitude': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := float64(parsed)
		aStartLatitude = converted
	}

	if _, ok := q["start_longitude"]; !ok {
		http.Error(w, "Parameter 'start_longitude' expected in query", http.StatusBadRequest)
		return
	}
	{
		parsed, err := strconv.ParseFloat(q.Get("start_longitude"), 64)
		if err != nil {
			http.Error(w, "Parameter 'start_longitude': "+err.Error(), http.StatusBadRequest)
			return
		}
		converted := float64(parsed)
		aStartLongitude = converted
	}

	if _, ok := q["customer_uuid"]; ok {
		val := q.Get("customer_uuid")
		aCustomerUuid = &val
	}

	if _, ok := q["product_id"]; ok {
		val := q.Get("product_id")
		aProductID = &val
	}

	h.EstimatesTime(w,
		r,
		aStartLatitude,
		aStartLongitude,
		aCustomerUuid,
		aProductID)
}

// WrapUpdateMe wraps the path `/me` with the method "patch".
//
// Path description:
// Update an User Profile.
func WrapUpdateMe(h Handler, w http.ResponseWriter, r *http.Request) {
	var aUpdateUser Profile

	if r.Body == nil {
		http.Error(w, "Parameter 'update_user' expected in body, but got no body", http.StatusBadRequest)
		return
	}
	{
		var err error
		r.Body = http.MaxBytesReader(w, r.Body, 1024*1024)
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "Body unreadable: "+err.Error(), http.StatusBadRequest)
			return
		}

		err = ValidateAgainstProfileSchema(body)
		if err != nil {
			http.Error(w, "Failed to validate against schema: "+err.Error(), http.StatusBadRequest)
			return
		}

		err = json.Unmarshal(body, &aUpdateUser)
		if err != nil {
			http.Error(w, "Error JSON-decoding body parameter 'update_user': "+err.Error(),
				http.StatusBadRequest)
			return
		}
	}

	h.UpdateMe(w,
		r,
		aUpdateUser)
}

// WrapUploadInfos wraps the path `/upload_infos` with the method "patch".
//
// Path description:
// Upload information about an User.
func WrapUploadInfos(h Handler, w http.ResponseWriter, r *http.Request) {
	h.UploadInfos(w, r)
}

// WrapHistory wraps the path `/history` with the method "get".
//
// Path description:
// The User Activity endpoint returns data about a user's lifetime activity with Uber. The response will
// include pickup locations and times, dropoff locations and times, the distance of past requests, and
// information about which products were requested.
func WrapHistory(h Handler, w http.ResponseWriter, r *http.Request) {
	var aOffset *int32
	var aLimit *int32

	q := r.URL.Query()

	if _, ok := q["offset"]; ok {
		{
			parsed, err := strconv.ParseInt(q.Get("offset"), 10, 32)
			if err != nil {
				http.Error(w, "Parameter 'offset': "+err.Error(), http.StatusBadRequest)
				return
			}
			converted := int32(parsed)
			aOffset = &converted
		}
	}

	if _, ok := q["limit"]; ok {
		{
			parsed, err := strconv.ParseInt(q.Get("limit"), 10, 32)
			if err != nil {
				http.Error(w, "Parameter 'limit': "+err.Error(), http.StatusBadRequest)
				return
			}
			converted := int32(parsed)
			aLimit = &converted
		}
	}

	h.History(w,
		r,
		aOffset,
		aLimit)
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
