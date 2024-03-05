import ndjsonStream from "can-ndjson-stream"
import { last } from "lodash-es"
import { useSession } from "next-auth/react"
import { useEffect, useRef, useState } from "react"

import { toast } from "react-hot-toast"

import { ICreatorRole, StreamingDataTypeEnum, StreamingSignalsEnum } from "~/api-client"
import { env } from "~/env.mjs"
import { useConversationStore, useMessageStore, useSettingStore } from "~/stores"
import { type Message } from "~/types"

import { generateUUID } from "~/utils"

import CancelMessageButton from "./CancelMessageButton"
import ClearConversationButton from "./ClearConversationButton"
import EmptyView from "./EmptyView"
import Header from "./Header"
import MessageTextarea from "./MessageTextarea"
import MessageView from "./MessageView"

const ConversationView = () => {
  const conversationStore = useConversationStore()
  const messageStore = useMessageStore()
  const settingsStore = useSettingStore()
  const { data: session } = useSession()
  const [isStickyAtBottom, setIsStickyAtBottom] = useState<boolean>(true)
  const conversationViewRef = useRef<HTMLDivElement>(null)
  const currentConversation = conversationStore.getConversationById(conversationStore.currentConversationId)
  const messageList = currentConversation
    ? messageStore.messageList.filter((message) => message.conversationId === currentConversation.id)
    : []
  const lastMessage = last(messageList)

  useEffect(() => {
    messageStore.messageList.map((message) => {
      if (message.status === "LOADING") {
        if (message.content === "") {
          messageStore.updateMessage(message.id, {
            content: "Failed to send the message.",
            status: "FAILED",
          })
        } else {
          messageStore.updateMessage(message.id, {
            status: "DONE",
          })
        }
      }
    })

    const handleConversationViewScroll = () => {
      if (!conversationViewRef.current) {
        return
      }
      setIsStickyAtBottom(
        conversationViewRef.current.scrollTop + conversationViewRef.current.clientHeight >=
          conversationViewRef.current.scrollHeight
      )
    }
    conversationViewRef.current?.addEventListener("scroll", handleConversationViewScroll)

    return () => {
      conversationViewRef.current?.removeEventListener("scroll", handleConversationViewScroll)
    }
  }, [])

  useEffect(() => {
    if (!conversationViewRef.current) {
      return
    }
    conversationViewRef.current.scrollTop = conversationViewRef.current.scrollHeight
  }, [currentConversation, lastMessage?.id])

  useEffect(() => {
    if (!conversationViewRef.current) {
      return
    }

    if (lastMessage?.status === "LOADING" && isStickyAtBottom) {
      conversationViewRef.current.scrollTop = conversationViewRef.current.scrollHeight
    }
  }, [lastMessage?.status, lastMessage?.content, isStickyAtBottom])

  const sendMessageToCurrentConversation = async () => {
    const currentConversation = conversationStore.getConversationById(
      conversationStore.getState().currentConversationId
    )
    if (!currentConversation) {
      return
    }
    if (lastMessage?.status === "LOADING") {
      return
    }

    const messageList = messageStore
      .getState()
      .messageList.filter((message) => message.conversationId === currentConversation.id)

    const message: Message = {
      id: generateUUID(),
      conversationId: currentConversation.id,
      creatorId: currentConversation.agentId,
      creatorRole: ICreatorRole.AGENT,
      createdAt: Date.now(),
      content: "",
      events: [],
      status: "LOADING",
    }
    messageStore.addMessage(message)

    let formatedMessageList = []
    for (let i = messageList.length - 1; i >= 0; i--) {
      const message = messageList[i] as Message
      const llmEvents = message.events.filter((event) => event.data_type === "llm")
      formatedMessageList.unshift({
        role: message.creatorRole,
        content: `${message.content}${llmEvents.map((event) => event.data).join("/n")}`,
      })
    }

    try {
      const rawRes = await fetch(`${env.NEXT_PUBLIC_API_URL}/chat/agent`, {
        method: "POST",
        body: JSON.stringify({
          messages: formatedMessageList,
          api_key: localStorage.getItem("openaiApiKey") || undefined,
          org_id: localStorage.getItem("openaiOrgId") || undefined,
          conversation_id: currentConversation.id,
          new_message_id: message.id,
          user_email: session?.user?.name || "no-auth",
          settings: {
            data: settingsStore.setting,
            version: settingsStore.setting.version,
          },
        }),
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      })

      if (!rawRes.ok) {
        console.error(rawRes)
        let errorMessage = "Failed to request message, please check your network."
        try {
          const res = await rawRes.json()
          errorMessage = res.error.message
        } catch (error) {
          // do nth
        }
        messageStore.updateMessage(message.id, {
          content: errorMessage,
          status: "FAILED",
        })
        return
      }

      // Handle successful response
      const data = rawRes.body
      if (!data) {
        toast.error("No data return")
        return
      }
      const reader = ndjsonStream(data).getReader()
      let done = false
      while (!done) {
        const { value, done: readerDone } = await reader.read()
        if (value) {
          const { data_type, data, metadata } = value
          if (data && data.length > 0) {
            if (data_type === StreamingDataTypeEnum.SIGNAL) {
              if (data === StreamingSignalsEnum.START) {
                message.runId = metadata?.run_id
              } else if (data === StreamingSignalsEnum.LLM_END) {
                message.events.push({
                  data_type: "llm",
                  data: message.content,
                  metadata: {},
                })
                message.content = ""
              } else {
                message.events.push(value)
              }
            } else if (data_type === "llm") {
              message.content = message.content + data
            } else {
              message.events.push(value)
            }
            messageStore.updateMessage(message.id, {
              content: message.content,
            })

            // Check if the message is cancelled
            const updatedStatus = messageStore.getState().messageList.find((m) => m.id === message.id)?.status
            if (updatedStatus === "CANCELLED") break
          }
        }
        done = readerDone
      }
      messageStore.updateMessage(message.id, {
        status: "DONE",
      })

      messageList.push(message)
    } catch (error: any) {
      // Handle any errors that occurred during the fetch request
      console.error("Error:", error.message)
    }
  }

  return (
    <div className="relative flex h-full max-h-full w-full flex-col items-start justify-start bg-neutral dark:bg-base-300">
      <Header />

      <div
        ref={conversationViewRef}
        className="relative flex h-full !max-h-[calc(100%-150px)] w-full flex-col items-start justify-start overflow-y-auto bg-neutral dark:bg-base-300"
      >
        <div className="h-auto w-full grow">
          {messageList.length === 0 || !currentConversation ? (
            <EmptyView className="mt-16 p-24" sendMessage={sendMessageToCurrentConversation} />
          ) : (
            messageList.map((message, idx) => (
              <MessageView
                key={message.id}
                message={message}
                isLatestMessage={idx === messageList.length - 1}
                conversationId={currentConversation.id}
              />
            ))
          )}
        </div>
      </div>

      <div className="absolute bottom-0 flex w-full flex-row items-center justify-center gap-csm !bg-neutral px-8 py-csm xl:px-16 dark:!bg-base-200">
        <ClearConversationButton />
        <MessageTextarea disabled={lastMessage?.status === "LOADING"} sendMessage={sendMessageToCurrentConversation} />
        <CancelMessageButton lastMessage={lastMessage} />
      </div>
    </div>
  )
}

export default ConversationView
