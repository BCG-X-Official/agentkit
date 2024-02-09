/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from "../core/CancelablePromise"
import { OpenAPI } from "../core/OpenAPI"
import { request as __request } from "../core/request"

export class DefaultService {
  /**
   * Root
   * An example "Hello world" FastAPI route.
   * @returns string Successful Response
   * @throws ApiError
   */
  public static rootGet(): CancelablePromise<Record<string, string>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/",
    })
  }
}
