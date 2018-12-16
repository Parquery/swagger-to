// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs/Rx';
import { RequestOptions } from '@angular/http';

export interface Product {
    // Unique identifier representing a specific product for a given latitude & longitude.
    // For example, uberX in San Francisco will have a different product_id than uberX in Los Angeles.
    product_id: string;

    // Description of product.
    desc: string;

    // Display name of product.
    display_name: string;

    // Capacity of product. For example, 4 people.
    capacity: number;

    // Image URL representing the product.
    image: string;
}

export interface ProductList {
    // Contains the list of products
    products: Array<Product>;
}

type ProductMap = Map<string, Product>;

export interface PriceEstimate {
    // Unique identifier representing a specific product for a given latitude & longitude. For example,
    // uberX in San Francisco will have a different product_id than uberX in Los Angeles
    product_id: string;

    // [ISO 4217](http://en.wikipedia.org/wiki/ISO_4217) currency code.
    currency_code: string;

    // Display name of product.
    display_name: string;

    // Formatted string of estimate in local currency of the start location.
    // Estimate could be a range, a single number (flat rate) or "Metered" for TAXI.
    estimate: string;

    // Lower bound of the estimated price.
    low_estimate?: number;

    // Upper bound of the estimated price.
    high_estimate?: number;

    // Expected surge multiplier. Surge is active if surge_multiplier is greater than 1.
    // Price estimate already factors in the surge multiplier.
    surge_multiplier?: number;
}

type PriceEstimateArray = Array<Product>;

export interface Profile {
    // First name of the Uber user.
    first_name?: string;

    // Last name of the Uber user.
    last_name: string;

    // Email address of the Uber user
    email: string;

    // Image URL of the Uber user.
    picture: string;

    // Promo code of the Uber user.
    promo_code?: string;
}

export interface Activity {
    // Unique identifier for the activity
    uuid: string;
}

export interface Activities {
    // Position in pagination.
    offset: number;

    // Number of items to retrieve (100 max).
    limit: number;

    // Total number of items available.
    count: number;

    history: Array<Activity>;
}

@Injectable()
export class RemoteCaller {
    public url_prefix: string;
    public on_error: (error: HttpErrorResponse) => Observable<HttpErrorResponse> | null;

    constructor(private http: Http) {
        this.url_prefix = "";
        this.on_error = null;
    }

    public set_url_prefix(url_prefix: string) {
        this.url_prefix = url_prefix;
    }

    public set_on_error(on_error: (error: HttpErrorResponse) => Observable<HttpErrorResponse> | null) {
        this.on_error = on_error;
    }

    // Sends a request to the endpoint: /products get
    //
    // The Products endpoint returns information about the Uber products offered at a given location.
    public products(latitude: number, longitude: number): Observable<Map<string, Product> | HttpErrorResponse> {
        let url = this.url_prefix + "products";
        url += "?";
        url += "latitude=" + encodeURIComponent(latitude.toString());

        url += "&longitude=" + encodeURIComponent(longitude.toString());

        let observable = this.http.get(url);
        let typed_observable = observable.map(res => (res.json() as Map<string, Product>));
        if (this.on_error) {
            return typed_observable.catch(err => this.on_error(err))
        }
        return typed_observable;
    }

    // Sends a request to the endpoint: /estimates/price/{start_latitude}/{start_longitude}/{end_latitude}/{end_longitude} get
    //
    // The Price Estimates endpoint returns an estimated price range for each product offered at a given
    // location. The price estimate is provided as a formatted string with the full price range and the localized
    // currency symbol.
    public estimates_price(
            start_latitude: number,
            start_longitude: number,
            end_latitude: number,
            end_longitude: number,
            max_lines?: number): Observable<Array<Product> | HttpErrorResponse> {
        let url = this.url_prefix;
        url += encodeURIComponent("estimates/price/");
        url += encodeURIComponent(start_latitude.toString());
        url += encodeURIComponent("/");
        url += encodeURIComponent(start_longitude.toString());
        url += encodeURIComponent("/");
        url += encodeURIComponent(end_latitude.toString());
        url += encodeURIComponent("/");
        url += encodeURIComponent(end_longitude.toString());

        url += "?";
        if (max_lines) {
            url += "max_lines=" + encodeURIComponent(max_lines.toString());
        }

        let observable = this.http.get(url);
        let typed_observable = observable.map(res => (res.json() as Array<Product>));
        if (this.on_error) {
            return typed_observable.catch(err => this.on_error(err))
        }
        return typed_observable;
    }

    // Sends a request to the endpoint: /estimates/time get
    //
    // The Time Estimates endpoint returns ETAs for all products.
    public estimates_time(
            start_latitude: number,
            start_longitude: number,
            customer_uuid?: string,
            product_id?: string): Observable<Map<string, Product> | HttpErrorResponse> {
        let url = this.url_prefix + "estimates/time";
        url += "?";
        url += "start_latitude=" + encodeURIComponent(start_latitude.toString());

        url += "&start_longitude=" + encodeURIComponent(start_longitude.toString());

        if (customer_uuid) {
            url += "&customer_uuid=" + encodeURIComponent(customer_uuid);
        }

        if (product_id) {
            url += "&product_id=" + encodeURIComponent(product_id);
        }

        let observable = this.http.get(url);
        let typed_observable = observable.map(res => (res.json() as Map<string, Product>));
        if (this.on_error) {
            return typed_observable.catch(err => this.on_error(err))
        }
        return typed_observable;
    }

    // Sends a request to the endpoint: /me patch
    //
    // Update an User Profile.
    public update_me(update_user: Profile): Observable<Profile | HttpErrorResponse> {
        const url = this.url_prefix + "me";

        let observable = this.http.request(url, 
            new RequestOptions({method: "patch", body: JSON.stringify(update_user)}));
        let typed_observable = observable.map(res => (res.json() as Profile));
        if (this.on_error) {
            return typed_observable.catch(err => this.on_error(err))
        }
        return typed_observable;
    }
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
