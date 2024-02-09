/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FeedbackLangchain } from "../models/FeedbackLangchain"
import type { IFeedback } from "../models/IFeedback"

import type { CancelablePromise } from "../core/CancelablePromise"
import { OpenAPI } from "../core/OpenAPI"
import { request as __request } from "../core/request"

export class StatisticsService {
  /**
   * Send Feedback
   * Send feedback to the Langsmith API.
   * @param requestBody
   * @returns FeedbackLangchain Successful Response
   * @throws ApiError
   */
  public static sendFeedbackApiV1StatisticsFeedbackPost(requestBody: IFeedback): CancelablePromise<FeedbackLangchain> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/statistics/feedback",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
