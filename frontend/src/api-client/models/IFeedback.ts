/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { UserSettings } from "./UserSettings"

export type IFeedback = {
  conversationId: string
  messageId: string
  user: string
  score: number
  comment: string
  key: string
  settings?: UserSettings | null
  previousId?: string | null
}
