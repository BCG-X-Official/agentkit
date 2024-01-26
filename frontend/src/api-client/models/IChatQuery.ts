/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { IChatMessage } from "./IChatMessage"
import type { UserSettings } from "./UserSettings"

export type IChatQuery = {
  messages: Array<IChatMessage>
  apiKey?: string | null
  conversationId: string
  newMessageId: string
  userEmail: string
  settings?: UserSettings | null
}
