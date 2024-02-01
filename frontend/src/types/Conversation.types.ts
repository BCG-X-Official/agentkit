import { type Id, type Timestamp } from "."

export interface Conversation {
  id: string
  connectionId?: Id
  databaseName?: string
  agentId: string
  title: string
  createdAt: Timestamp
}
