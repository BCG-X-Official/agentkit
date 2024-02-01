import { merge } from "lodash-es"
import { create } from "zustand"
import { persist } from "zustand/middleware"
import { type Timestamp } from "@/types"

interface ExecuteQueryContext {
  statement: string
  messageId: string
  conversationId: string
}

interface QueryExecution {
  statement: string
  resultRow?: Record<string, any>
  createdAt: Timestamp
  messageId: string
  conversationId: string
}

interface QueryCache {
  [statement: string]: QueryExecution
}

interface QueryState {
  showDrawer: boolean
  queryCache: QueryCache
  context?: ExecuteQueryContext
  getState: () => QueryState
  toggleDrawer: (show?: boolean) => void
  setContext: (context: ExecuteQueryContext | undefined) => void
  setQueryCache: (query: string, resultRows: Record<string, any>[], messageId: string, conversationId: string) => void
  getQueryCacheAll: () => QueryCache
  resetQueryCache: () => void
}

export const useQueryStore = create<QueryState>()(
  persist(
    (set, get) => ({
      showDrawer: false,
      queryCache: {},
      getState: () => get(),
      toggleDrawer: (show) => {
        set((state) => ({
          ...state,
          showDrawer: show ?? !state.showDrawer,
        }))
      },
      setContext: (context) => {
        set((state) => ({
          ...state,
          context,
        }))
      },
      setQueryCache: (query, resultRows, messageId, conversationId) => {
        set((state) => ({
          ...state,
          queryCache: {
            ...state.queryCache,
            [`${conversationId}_${messageId}_${query}`]: {
              statement: query,
              resultRow: resultRows.length > 0 ? resultRows[0] : undefined,
              createdAt: Date.now(),
              messageId: messageId,
              conversationId: conversationId,
            },
          },
        }))
      },
      getQueryCacheAll: () => {
        return get().queryCache
      },
      resetQueryCache: () => {
        set((state) => ({
          ...state,
          queryCache: {},
        }))
      },
    }),
    {
      name: "query-storage",
      merge: (persistedState, currentState) => {
        return {
          ...merge(currentState, persistedState),
          context: undefined,
        }
      },
    }
  )
)
