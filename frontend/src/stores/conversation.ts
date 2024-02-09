import dayjs from "dayjs"
import { create } from "zustand"
import { persist } from "zustand/middleware"
import { type Conversation, type Id } from "@/types"
import { generateUUID } from "@/utils"

const getDefaultConversation = (): Conversation => {
  return {
    id: generateUUID(),
    agentId: "gpt-4",
    title: dayjs().format("LTS"),
    createdAt: Date.now(),
  }
}

interface ConversationState {
  getState: () => ConversationState
  conversationList: Conversation[]
  currentConversationId?: Id
  createConversation: (connectionId?: Id, databaseName?: string) => Conversation
  setCurrentConversationId: (conversationId: Id | undefined) => void
  getConversationById: (conversationId: Id | undefined) => Conversation | undefined
  updateConversation: (conversationId: Id, conversation: Partial<Conversation>) => void
  clearConversation: (filter: (conversation: Conversation) => boolean) => void
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set, get) => ({
      getState: () => get(),
      conversationList: [],
      createConversation: (connectionId?: Id, databaseName?: string) => {
        const conversation: Conversation = {
          ...getDefaultConversation(),
          connectionId,
          databaseName,
        }
        if (connectionId) {
          conversation.agentId = "gpt-4"
        }
        set((state) => ({
          conversationList: [...state.conversationList, conversation],
          currentConversationId: conversation.id,
        }))
        return conversation
      },
      setCurrentConversationId: (conversation: Id | undefined) => set(() => ({ currentConversationId: conversation })),
      getConversationById: (conversationId: Id | undefined) => {
        return get().conversationList.find((item) => item.id === conversationId)
      },
      updateConversation: (conversationId: Id, conversation: Partial<Conversation>) => {
        set((state) => ({
          ...state,
          conversationList: state.conversationList.map((item) =>
            item.id === conversationId ? { ...item, ...conversation } : item
          ),
        }))
      },
      clearConversation: (filter: (conversation: Conversation) => boolean) => {
        set((state) => ({
          ...state,
          conversationList: state.conversationList.filter(filter),
        }))
      },
    }),
    {
      name: "conversation-storage",
      version: 1,
      migrate: (persistedState: any, version: number) => {
        let state = persistedState as ConversationState
        if (version === 0) {
          for (const conversation of state.conversationList) {
            if (!conversation.connectionId) {
              conversation.agentId = "general-bot"
            } else {
              conversation.agentId = "sql-chat-bot"
            }
          }
          state.currentConversationId = undefined
        }

        return state
      },
    }
  )
)
