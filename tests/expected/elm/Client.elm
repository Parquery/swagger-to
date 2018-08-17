-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!


module Client 
    exposing
        ( Activities
        , Activity
        , PriceEstimate
        , PriceEstimateArray
        , Product
        , ProductList
        , ProductMap
        , Profile
        , decodeActivities
        , decodeActivity
        , decodePriceEstimate
        , decodePriceEstimateArray
        , decodeProduct
        , decodeProductList
        , decodeProductMap
        , decodeProfile
        , encodeActivities
        , encodeActivity
        , encodePriceEstimate
        , encodePriceEstimateArray
        , encodeProduct
        , encodeProductList
        , encodeProductMap
        , encodeProfile
        , estimatesPriceRequest
        , estimatesTimeRequest
        , productsRequest
        , updateMeRequest
        )

import Dict exposing (Dict)
import Http
import Json.Decode
import Json.Decode.Pipeline
import Json.Encode
import Json.Encode.Extra
import QueryString
import Time


-- Models


type alias Product = 
    -- Unique identifier representing a specific product for a given latitude & longitude.
    -- For example, uberX in San Francisco will have a different product_id than uberX in Los Angeles.
    { productID : String
    -- Description of product.
    , desc : String
    -- Display name of product.
    , displayName : String
    -- Capacity of product. For example, 4 people.
    , capacity : Int
    -- Image URL representing the product.
    , image : String
    }


type alias ProductList = 
    -- Contains the list of products
    { products : List Product
    }


type alias ProductMap = 
    Dict String Product


type alias PriceEstimate = 
    -- Unique identifier representing a specific product for a given latitude & longitude. For example,
    -- uberX in San Francisco will have a different product_id than uberX in Los Angeles
    { productID : String
    -- [ISO 4217](http://en.wikipedia.org/wiki/ISO_4217) currency code.
    , currencyCode : String
    -- Display name of product.
    , displayName : String
    -- Formatted string of estimate in local currency of the start location.
    -- Estimate could be a range, a single number (flat rate) or "Metered" for TAXI.
    , estimate : String
    -- Lower bound of the estimated price.
    , lowEstimate : Maybe (Float)
    -- Upper bound of the estimated price.
    , highEstimate : Maybe (Float)
    -- Expected surge multiplier. Surge is active if surge_multiplier is greater than 1.
    -- Price estimate already factors in the surge multiplier.
    , surgeMultiplier : Maybe (Float)
    }


type alias PriceEstimateArray = 
    List Product


type alias Profile = 
    -- First name of the Uber user.
    { firstName : Maybe (String)
    -- Last name of the Uber user.
    , lastName : String
    -- Email address of the Uber user
    , email : String
    -- Image URL of the Uber user.
    , picture : String
    -- Promo code of the Uber user.
    , promoCode : Maybe (String)
    }


type alias Activity = 
    -- Unique identifier for the activity
    { uuid : String
    }


type alias Activities = 
    -- Position in pagination.
    { offset : Int
    -- Number of items to retrieve (100 max).
    , limit : Int
    -- Total number of items available.
    , count : Int
    , history : List Activity
    }


-- Encoders


encodeProduct : Product -> Json.Encode.Value
encodeProduct aProduct =
    Json.Encode.object
        [ ( "product_id", Json.Encode.string <| aProduct.productID )
        , ( "desc", Json.Encode.string <| aProduct.desc )
        , ( "display_name", Json.Encode.string <| aProduct.displayName )
        , ( "capacity", Json.Encode.int <| aProduct.capacity )
        , ( "image", Json.Encode.string <| aProduct.image )
        ]


encodeProductList : ProductList -> Json.Encode.Value
encodeProductList aProductList =
    Json.Encode.object
        [ ( "products", Json.Encode.list <| List.map encodeProduct <| aProductList.products )
        ]


encodeProductMap : (Dict String Product) -> Json.Encode.Value 
encodeProductMap aProductMap =
    Json.Encode.Extra.dict identity encodeProduct <| aProductMap


encodePriceEstimate : PriceEstimate -> Json.Encode.Value
encodePriceEstimate aPriceEstimate =
    Json.Encode.object
        [ ( "product_id", Json.Encode.string <| aPriceEstimate.productID )
        , ( "currency_code", Json.Encode.string <| aPriceEstimate.currencyCode )
        , ( "display_name", Json.Encode.string <| aPriceEstimate.displayName )
        , ( "estimate", Json.Encode.string <| aPriceEstimate.estimate )
        , ( "low_estimate", Json.Encode.Extra.maybe (Json.Encode.float) <| aPriceEstimate.lowEstimate )
        , ( "high_estimate", Json.Encode.Extra.maybe (Json.Encode.float) <| aPriceEstimate.highEstimate )
        , ( "surge_multiplier", Json.Encode.Extra.maybe (Json.Encode.float) <| aPriceEstimate.surgeMultiplier )
        ]


encodePriceEstimateArray : (List Product) -> Json.Encode.Value 
encodePriceEstimateArray aPriceEstimateArray =
    Json.Encode.list <| List.map encodeProduct <| aPriceEstimateArray


encodeProfile : Profile -> Json.Encode.Value
encodeProfile aProfile =
    Json.Encode.object
        [ ( "first_name", Json.Encode.Extra.maybe (Json.Encode.string) <| aProfile.firstName )
        , ( "last_name", Json.Encode.string <| aProfile.lastName )
        , ( "email", Json.Encode.string <| aProfile.email )
        , ( "picture", Json.Encode.string <| aProfile.picture )
        , ( "promo_code", Json.Encode.Extra.maybe (Json.Encode.string) <| aProfile.promoCode )
        ]


encodeActivity : Activity -> Json.Encode.Value
encodeActivity aActivity =
    Json.Encode.object
        [ ( "uuid", Json.Encode.string <| aActivity.uuid )
        ]


encodeActivities : Activities -> Json.Encode.Value
encodeActivities aActivities =
    Json.Encode.object
        [ ( "offset", Json.Encode.int <| aActivities.offset )
        , ( "limit", Json.Encode.int <| aActivities.limit )
        , ( "count", Json.Encode.int <| aActivities.count )
        , ( "history", Json.Encode.list <| List.map encodeActivity <| aActivities.history )
        ]


-- Decoders


decodeProduct : Json.Decode.Decoder Product
decodeProduct =
    Json.Decode.Pipeline.decode Product
        |> Json.Decode.Pipeline.required "product_id" Json.Decode.string
        |> Json.Decode.Pipeline.required "desc" Json.Decode.string
        |> Json.Decode.Pipeline.required "display_name" Json.Decode.string
        |> Json.Decode.Pipeline.required "capacity" Json.Decode.int
        |> Json.Decode.Pipeline.required "image" Json.Decode.string



decodeProductList : Json.Decode.Decoder ProductList
decodeProductList =
    Json.Decode.Pipeline.decode ProductList
        |> Json.Decode.Pipeline.required "products" (Json.Decode.list <| decodeProduct)



decodeProductMap : Json.Decode.Decoder (Dict String Product)
decodeProductMap =
    Json.Decode.dict <| decodeProduct


decodePriceEstimate : Json.Decode.Decoder PriceEstimate
decodePriceEstimate =
    Json.Decode.Pipeline.decode PriceEstimate
        |> Json.Decode.Pipeline.required "product_id" Json.Decode.string
        |> Json.Decode.Pipeline.required "currency_code" Json.Decode.string
        |> Json.Decode.Pipeline.required "display_name" Json.Decode.string
        |> Json.Decode.Pipeline.required "estimate" Json.Decode.string
        |> Json.Decode.Pipeline.optional "low_estimate" (Json.Decode.nullable Json.Decode.float) Nothing
        |> Json.Decode.Pipeline.optional "high_estimate" (Json.Decode.nullable Json.Decode.float) Nothing
        |> Json.Decode.Pipeline.optional "surge_multiplier" (Json.Decode.nullable Json.Decode.float) Nothing



decodePriceEstimateArray : Json.Decode.Decoder (List Product)
decodePriceEstimateArray =
    Json.Decode.list <| decodeProduct


decodeProfile : Json.Decode.Decoder Profile
decodeProfile =
    Json.Decode.Pipeline.decode Profile
        |> Json.Decode.Pipeline.optional "first_name" (Json.Decode.nullable Json.Decode.string) Nothing
        |> Json.Decode.Pipeline.required "last_name" Json.Decode.string
        |> Json.Decode.Pipeline.required "email" Json.Decode.string
        |> Json.Decode.Pipeline.required "picture" Json.Decode.string
        |> Json.Decode.Pipeline.optional "promo_code" (Json.Decode.nullable Json.Decode.string) Nothing



decodeActivity : Json.Decode.Decoder Activity
decodeActivity =
    Json.Decode.Pipeline.decode Activity
        |> Json.Decode.Pipeline.required "uuid" Json.Decode.string



decodeActivities : Json.Decode.Decoder Activities
decodeActivities =
    Json.Decode.Pipeline.decode Activities
        |> Json.Decode.Pipeline.required "offset" Json.Decode.int
        |> Json.Decode.Pipeline.required "limit" Json.Decode.int
        |> Json.Decode.Pipeline.required "count" Json.Decode.int
        |> Json.Decode.Pipeline.required "history" (Json.Decode.list <| decodeActivity)



-- Remote Calls



{-| Contains a "get" request to the endpoint: /products, to be sent with Http.send
    
    The Products endpoint returns information about the Uber products offered at a given location.
-}
productsRequest : String -> Maybe Time.Time -> Bool -> Float -> Float -> Http.Request (Dict String Product)
productsRequest prefix maybeTimeout withCredentials latitude longitude =
    let
        baseUrl = prefix ++ "products"
        queryString = QueryString.empty
            |> QueryString.add "latitude" (toString latitude)
            |> QueryString.add "longitude" (toString longitude)
        url = baseUrl ++ (QueryString.render queryString)
    in
    Http.request
        { body = Http.emptyBody
        , expect = Http.expectJson (Json.Decode.dict <| decodeProduct)
        , headers = []
        , method = "GET"
        , timeout = maybeTimeout
        , url = url
        , withCredentials = withCredentials
        }


{-| Contains a "get" request to the endpoint: /estimates/price/{start_latitude}/{start_longitude}/{end_latitude}/{end_longitude}, to be sent with Http.send
    
    The Price Estimates endpoint returns an estimated price range for each product offered at a given
    location. The price estimate is provided as a formatted string with the full price range and the localized
    currency symbol.
-}
estimatesPriceRequest :
    String
    -> Maybe Time.Time
    -> Bool
    -> Float
    -> Float
    -> Float
    -> Float
    -> Maybe Int
    -> Http.Request (List Product)
estimatesPriceRequest
    prefix
    maybeTimeout
    withCredentials
    startLatitude
    startLongitude
    endLatitude
    endLongitude
    maybeMaxLines =
        let
            baseUrl = prefix
                ++ "estimates/price/"
                ++ (toString startLatitude)
                ++ "/"
                ++ (toString startLongitude)
                ++ "/"
                ++ (toString endLatitude)
                ++ "/"
                ++ (toString endLongitude)
            queryString = QueryString.empty
                |> \queryStr -> Maybe.withDefault queryStr (Maybe.map 
                    (\var -> QueryString.add "max_lines" (toString var) queryStr) maybeMaxLines)
            url = baseUrl ++ (QueryString.render queryString)
        in
        Http.request
            { body = Http.emptyBody
            , expect = Http.expectJson (Json.Decode.list <| decodeProduct)
            , headers = []
            , method = "GET"
            , timeout = maybeTimeout
            , url = url
            , withCredentials = withCredentials
            }


{-| Contains a "get" request to the endpoint: /estimates/time, to be sent with Http.send
    
    The Time Estimates endpoint returns ETAs for all products.
-}
estimatesTimeRequest :
    String
    -> Maybe Time.Time
    -> Bool
    -> Float
    -> Float
    -> Maybe String
    -> Maybe String
    -> Http.Request (Dict String Product)
estimatesTimeRequest prefix maybeTimeout withCredentials startLatitude startLongitude maybeCustomerUuid maybeProductID =
    let
        baseUrl = prefix ++ "estimates/time"
        queryString = QueryString.empty
            |> QueryString.add "start_latitude" (toString startLatitude)
            |> QueryString.add "start_longitude" (toString startLongitude)
            |> \queryStr -> Maybe.withDefault queryStr (Maybe.map 
                (\var -> QueryString.add "customer_uuid" var queryStr) maybeCustomerUuid)
            |> \queryStr -> Maybe.withDefault queryStr (Maybe.map 
                (\var -> QueryString.add "product_id" var queryStr) maybeProductID)
        url = baseUrl ++ (QueryString.render queryString)
    in
    Http.request
        { body = Http.emptyBody
        , expect = Http.expectJson (Json.Decode.dict <| decodeProduct)
        , headers = []
        , method = "GET"
        , timeout = maybeTimeout
        , url = url
        , withCredentials = withCredentials
        }


{-| Contains a "patch" request to the endpoint: /me, to be sent with Http.send
    
    Update an User Profile.
-}
updateMeRequest : String -> Maybe Time.Time -> Bool -> Profile -> Http.Request Profile
updateMeRequest prefix maybeTimeout withCredentials updateUser =
    let
        url = prefix ++ "me"
    in
    Http.request
        { body = (encodeProfile updateUser) |> Http.jsonBody
        , expect = Http.expectJson decodeProfile
        , headers = []
        , method = "PATCH"
        , timeout = maybeTimeout
        , url = url
        , withCredentials = withCredentials
        }



-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
