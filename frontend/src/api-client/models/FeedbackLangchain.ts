/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { FeedbackSourceBaseLangchain } from "./FeedbackSourceBaseLangchain"

/**
 * Schema for getting feedback, copy of langchain Feedback type (pydantic v2).
 */
export type FeedbackLangchain = {
  id: string
  created_at: string
  modified_at: string
  run_id: string
  key: string
  score?: boolean | number | null
  value?: Record<string, any> | boolean | number | string | null
  comment?: string | null
  correction?: string | Record<string, any> | null
  feedback_source?: FeedbackSourceBaseLangchain | null
}
