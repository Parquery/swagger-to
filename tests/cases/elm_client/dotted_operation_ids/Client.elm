-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!


module Client 
    exposing
        ( getFooRequest
        )

import Dict exposing (Dict)
import Http
import Json.Decode
import Json.Decode.Pipeline
import Json.Encode
import Json.Encode.Extra
import Time


-- Remote Calls



{-| Contains a "get" request to the endpoint: `/api/v1/foo/{foo_id}`, to be sent with Http.send
-}
getFooRequest : String -> Maybe Time.Time -> Bool -> String -> Http.Request String
getFooRequest prefix maybeTimeout withCredentials fooID =
    let
        url = prefix
            ++ "api/v1/foo/"
            ++ fooID    in
    Http.request
        { body = Http.emptyBody
        , expect = Http.expectString
        , headers = []
        , method = "GET"
        , timeout = maybeTimeout
        , url = url
        , withCredentials = withCredentials
        }



-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
