import { type FeedbackLangchain, type ICreatorRole } from "~/api-client"

import { type Id, type Timestamp } from "."

type MessageStatus = "LOADING" | "DONE" | "FAILED" | "CANCELLED"

export interface MessageEvent {
  data: string
  data_type: string
  metadata: { [key: string]: string }
}

export interface ToolAppendixData {
  value: string
  language: string
  title: string
  event: MessageEvent
}

export interface Message {
  id: Id
  conversationId: string
  creatorId: Id
  creatorRole: ICreatorRole
  createdAt: Timestamp
  content: string
  events: MessageEvent[]
  status: MessageStatus
  feedback?: FeedbackLangchain
  runId?: string
}
