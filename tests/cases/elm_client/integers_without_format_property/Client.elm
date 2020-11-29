-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!


module Client 
    exposing
        ( MyType
        , decodeMyType
        , encodeMyType
        , getFooRequest
        )

import Dict exposing (Dict)
import Http
import Json.Decode
import Json.Decode.Pipeline
import Json.Encode
import Json.Encode.Extra
import Time


-- Models


type alias MyType = 
    { prop : Maybe (Int)
    }


-- Encoders


encodeMyType : MyType -> Json.Encode.Value
encodeMyType aMyType =
    Json.Encode.object
        [ ( "prop", Json.Encode.Extra.maybe (Json.Encode.int) <| aMyType.prop )
        ]


-- Decoders


decodeMyType : Json.Decode.Decoder MyType
decodeMyType =
    Json.Decode.Pipeline.decode MyType
        |> Json.Decode.Pipeline.optional "prop" (Json.Decode.nullable Json.Decode.int) Nothing



-- Remote Calls



{-| Contains a "get" request to the endpoint: `/`, to be sent with Http.send
-}
getFooRequest : String -> Maybe Time.Time -> Bool -> Http.Request String
getFooRequest prefix maybeTimeout withCredentials =
    let
        url = prefix ++ ""
    in
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
