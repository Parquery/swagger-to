// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!

import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs/Rx';
import { RequestOptions } from '@angular/http';

// is an identifiable primitive definition.
type Capacity = number;

// is a product summary object.
export interface ProductSummary {
    // is a test string property.
    product_id: string;

    metadata?: unknown;

    capacity?: number;
}

// is a product detail
export interface ProductDetail {
    // is a test string property.
    product_id: string;

    capacity?: number;

    metadata: unknown;

    data: unknown;
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
    // describe products
    public list_products(with_attributes?: boolean): Observable<ProductSummary | HttpErrorResponse> {
        let url = this.url_prefix + "products";
        url += "?";
        if (with_attributes) {
            url += "with_attributes=" + encodeURIComponent(with_attributes.toString());
        }

        let observable = this.http.get(url);
        let typed_observable = observable.map(res => (res.json() as ProductSummary));
        if (this.on_error) {
            return typed_observable.catch(err => this.on_error(err))
        }
        return typed_observable;
    }

    // Sends a request to the endpoint: /products/{id} get
    //
    // product detail
    public get_product(id: string): Observable<ProductDetail | HttpErrorResponse> {
        let url = this.url_prefix;
        url += encodeURIComponent("products/");
        url += encodeURIComponent(id);
        let observable = this.http.get(url);
        let typed_observable = observable.map(res => (res.json() as ProductDetail));
        if (this.on_error) {
            return typed_observable.catch(err => this.on_error(err))
        }
        return typed_observable;
    }
}

// Automatically generated file by swagger_to. DO NOT EDIT OR APPEND ANYTHING!
