-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!


module Client 
    exposing
        ( MyType
        , SubType
        , decodeMyType
        , decodeSubType
        , encodeMyType
        , encodeSubType
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
    { myInteger : Maybe (Int)
    }


type alias SubType = 
    { myInteger : Maybe (Int)
    , subProperty : Maybe (Int)
    }


-- Encoders


encodeMyType : MyType -> Json.Encode.Value
encodeMyType aMyType =
    Json.Encode.object
        [ ( "my_integer", Json.Encode.Extra.maybe (Json.Encode.int) <| aMyType.myInteger )
        ]


encodeSubType : SubType -> Json.Encode.Value
encodeSubType aSubType =
    Json.Encode.object
        [ ( "my_integer", Json.Encode.Extra.maybe (Json.Encode.int) <| aSubType.myInteger )
        , ( "sub_property", Json.Encode.Extra.maybe (Json.Encode.int) <| aSubType.subProperty )
        ]


-- Decoders


decodeMyType : Json.Decode.Decoder MyType
decodeMyType =
    Json.Decode.Pipeline.decode MyType
        |> Json.Decode.Pipeline.optional "my_integer" (Json.Decode.nullable Json.Decode.int) Nothing



decodeSubType : Json.Decode.Decoder SubType
decodeSubType =
    Json.Decode.Pipeline.decode SubType
        |> Json.Decode.Pipeline.optional "my_integer" (Json.Decode.nullable Json.Decode.int) Nothing
        |> Json.Decode.Pipeline.optional "sub_property" (Json.Decode.nullable Json.Decode.int) Nothing



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
