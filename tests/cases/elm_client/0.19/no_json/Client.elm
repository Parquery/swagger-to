-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!


module Client 
    exposing
        ( deleteHistoryRequest
        , updateMeRequest
        )

import Dict exposing (Dict)
import Http
import Json.Decode
import Json.Decode.Pipeline
import Json.Encode
import Json.Encode.Extra
import Time


-- Remote Calls



{-| Contains a "patch" request to the endpoint: `/me`, to be sent with Http.send
    
    Update an User Profile.
-}
updateMeRequest : String -> Maybe Time.Time -> Bool -> String -> Http.Request String
updateMeRequest prefix maybeTimeout withCredentials username =
    let
        baseUrl = prefix ++ "me"
        queryString = 
            paramsToQuery
                [ ("username", username)
                ]
                []
        url = baseUrl ++ queryString
    in
    Http.request
        { body = Http.emptyBody
        , expect = Http.expectString
        , headers = []
        , method = "PATCH"
        , timeout = maybeTimeout
        , url = url
        , withCredentials = withCredentials
        }


{-| Contains a "delete" request to the endpoint: `/history`, to be sent with Http.send
    
    Instructs the Back End to delete all the history about a user.
-}
deleteHistoryRequest : String -> Maybe Time.Time -> Bool -> Maybe String -> Http.Request String
deleteHistoryRequest prefix maybeTimeout withCredentials maybeUsername =
    let
        baseUrl = prefix ++ "history"
        queryString = 
            paramsToQuery
                []
                [ ("username", maybeUsername)
                ]
        url = baseUrl ++ queryString
    in
    Http.request
        { body = Http.emptyBody
        , expect = Http.expectString
        , headers = []
        , method = "DELETE"
        , timeout = maybeTimeout
        , url = url
        , withCredentials = withCredentials
        }



{-| Translates a list of (name, parameter) and a list of (name, optional parameter) to a
well-formatted query string.
-}
paramsToQuery : List ( String, String ) -> List ( String, Maybe String ) -> String
paramsToQuery params maybeParams =

    let
        queryParams : List Url.Builder.QueryParameter
        queryParams =
            List.map (\( name, value ) -> Url.Builder.string name value) params

        filteredParams : List Url.Builder.QueryParameter
        filteredParams =
            List.filter (\( _, maybeValue ) -> maybeValue /= Nothing) maybeParams
                |> List.map (\( name, maybeValue ) -> ( name, Maybe.withDefault "" maybeValue ))
                |> List.map (\( name, value ) ->  Url.Builder.string name value)
    in
    List.concat [ queryParams, filteredParams ]
    |> Url.Builder.toQuery
-- Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
