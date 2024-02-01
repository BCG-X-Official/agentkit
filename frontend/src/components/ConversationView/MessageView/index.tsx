import dayjs from "dayjs"
import { motion } from "framer-motion"
import Image from "next/image"
import { useSession } from "next-auth/react"
import { useMemo, useState } from "react"

import Avatar from "react-avatar"
import { Collapse } from "react-collapse"
import { toast } from "react-hot-toast"
import { Dropdown, DropdownItem, Tooltip } from "~/components/Common"
import Icon from "~/components/CustomIcons/Icon"

import ToolAppendixRenderer from "~/components/ToolAppendixRenderer"
import { env } from "~/env.mjs"
import { useMessageStore, useUserStore } from "~/stores"
import {
  type Message,
  type MessageEvent as MessageEventT,
  SUPPORTED_SYNTAX_LANGUAGES,
  type ToolAppendixData,
} from "~/types"

import { groupBy } from "~/utils"

import FeedbackView from "./FeedbackView"
import { MessageEvent } from "./MessageEvents/MessageEvent"
import { LLMResponse } from "./MessageEvents/MessageEvent/LLMResponse"
import { MessageEvents } from "./MessageEvents/MessageEvents"
import ThreeDotsLoader from "../../CustomIcons/ThreeDotsLoader"
import { CONVERSATION_VIEW_SELECTORS } from "../ConversationView.selectors"

interface Props {
  message: Message
  isLatestMessage: boolean
  conversationId: string
}

const MessageView = (props: Props) => {
  const { message, isLatestMessage, conversationId } = props
  const userStore = useUserStore()
  const messageStore = useMessageStore()
  const [isActionsCollapsed, setIsActionsCollapsed] = useState(true)
  const isCurrentUser = message.creatorId === userStore.currentUser.id
  const { data: session } = useSession()
  const showFeedback = env.NEXT_PUBLIC_ENABLE_MESSAGE_FEEDBACK

  const copyMessage = () => {
    navigator.clipboard.writeText(message.content)
    toast.success("Copied to clipboard")
  }

  const deleteMessage = (message: Message) => {
    messageStore.clearMessage((item) => item.id !== message.id)
  }

  const appendixEvents = useMemo(() => {
    const appendixEvents = [] as ToolAppendixData[]

    Object.values(SUPPORTED_SYNTAX_LANGUAGES).forEach((language) => {
      const regex = new RegExp("```" + language + "([\\s\\S]*?)```", "g")
      let match
      let idx = 1

      message.events
        .filter((e) => e.data_type === "appendix")
        .forEach((event) => {
          while ((match = regex.exec(event.data)) !== null) {
            appendixEvents.push({
              value: (match[1] as string).replace("\n", " ").trim(),
              language: language,
              title: event.metadata.title || `Appendix ${idx}`,
              event: event,
            })
            idx += 1
          }
        })
    })

    return appendixEvents
  }, [message.events.length])

  const [groupedToolEvents, otherEvents] = useMemo(() => {
    return [
      groupBy(
        message.events.filter((e) => !!e.metadata.tool),
        "metadata.tool"
      ) as { [key: string]: MessageEventT[] },
      message.events.filter((e) => !e.metadata.tool),
    ]
  }, [message.events.length])

  const isRecentMessage = useMemo(() => {
    const minutesBefore = new Date()
    minutesBefore.setMinutes(minutesBefore.getMinutes() - 5)
    return isLatestMessage && dayjs(message.createdAt).isAfter(dayjs(minutesBefore))
  }, [isLatestMessage, message.createdAt])

  return (
    <div
      className={`group mx-auto flex w-full max-w-full flex-row items-start justify-start bg-neutral px-8 py-4 xl:px-16 dark:bg-base-300 ${
        isCurrentUser ? "justify-start !bg-base-100 pb-8 pt-6" : ""
      }`}
      data-cy={CONVERSATION_VIEW_SELECTORS.filledChatMessageAreaWrapper}
    >
      {isCurrentUser ? (
        <>
          <div className="mr-2 flex h-10 w-10 shrink-0 items-center justify-center rounded-full [&_span]:!text-neutral">
            {session?.user?.name ? (
              <div data-cy={CONVERSATION_VIEW_SELECTORS.userAvatar} className="h-full w-full">
                <Avatar name={session.user.name.replace("-", " ")} size="40" round={true} />
              </div>
            ) : (
              <Icon.AiOutlineUser className="h-6 w-6" />
            )}
          </div>
          <div className="flex w-auto max-w-[calc(100%-2rem)] flex-col items-start justify-start">
            <div className="w-full whitespace-pre-wrap break-all rounded-lg bg-transparent px-4 py-2">
              <p data-cy={CONVERSATION_VIEW_SELECTORS.userMessage}>{message.content}</p>
            </div>
          </div>
          <div className="invisible group-hover:visible">
            <Dropdown
              tigger={
                <button className="ml-1 mt-2 flex h-6 w-6 shrink-0 items-center justify-center">
                  <Icon.IoMdMore className="h-auto w-5 text-base-300 dark:!text-neutral" />
                </button>
              }
            >
              <div className="flex flex-col items-start justify-start rounded-lg bg-base-100 p-1">
                <DropdownItem
                  className="flex w-full cursor-pointer flex-row items-center justify-start rounded-lg p-1 px-2 hover:bg-neutral dark:hover:bg-accent"
                  onClick={copyMessage}
                >
                  <Icon.BiClipboard className="mr-2 h-auto w-4 opacity-70" />
                  Copy
                </DropdownItem>
                <DropdownItem
                  className="flex w-full cursor-pointer flex-row items-center justify-start rounded-lg p-1 px-2 hover:bg-neutral dark:hover:bg-accent"
                  onClick={() => deleteMessage(message)}
                >
                  <Icon.BiTrash className="mr-2 h-auto w-4 opacity-70" />
                  Delete
                </DropdownItem>
              </div>
            </Dropdown>
          </div>
        </>
      ) : (
        <>
          <div className="mr-2 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-gray-950">
            <Image src="/logo.png" width="25" height="25" alt="agent" />
          </div>
          {message.status === "LOADING" && message.content === "" && message.events.length === 0 ? (
            <div
              className="mt-0.5 w-12 rounded-lg bg-transparent px-4 py-2 dark:bg-transparent"
              data-cy={CONVERSATION_VIEW_SELECTORS.stepsLoading}
            >
              <ThreeDotsLoader />
            </div>
          ) : (
            <>
              <div
                className="flex w-full max-w-[calc(100%-2rem)] flex-col items-start justify-start bg-transparent"
                data-cy={CONVERSATION_VIEW_SELECTORS.stepsWrapper}
              >
                <div
                  className={`prose prose-neutral w-full max-w-full rounded-lg bg-transparent px-4 py-2 text-base-300 dark:bg-transparent dark:text-base-300 ${
                    message.status === "FAILED" && "border border-red-400 bg-red-100 text-red-500"
                  }`}
                >
                  <div className="rounded-lg border-accent  bg-primary/30">
                    <div className="flex items-center justify-start">
                      <div className="my-1 ml-2">
                        <Icon.TbListDetails className="h-auto w-6 text-accent" />
                      </div>
                      <div className="my-1 ml-1">
                        <span className="text-lg text-neutral">Steps</span>
                      </div>
                      {message.status === "LOADING" && (
                        <div className="my-1 ml-2" data-cy={CONVERSATION_VIEW_SELECTORS.stepsLoading}>
                          <ThreeDotsLoader />
                        </div>
                      )}
                      <div className="my-1 ml-auto mr-2">
                        <Tooltip content={isActionsCollapsed ? "Show steps" : "Hide steps"} position="daisytooltip-top">
                          <button
                            className="flex h-6 w-6 items-center justify-center rounded bg-accent bg-none p-1 text-xs opacity-90 hover:opacity-100"
                            onClick={() => setIsActionsCollapsed(!isActionsCollapsed)}
                          >
                            {isActionsCollapsed ? (
                              <Icon.BiChevronDown className="h-auto w-full !text-base-300 dark:!text-neutral" />
                            ) : (
                              <Icon.BiChevronUp className="h-auto w-full !text-base-300 dark:!text-neutral" />
                            )}
                          </button>
                        </Tooltip>
                      </div>
                    </div>
                    <Collapse isOpened={!isActionsCollapsed}>
                      <div className="m-1 border-t-2 border-dashed border-gray-400 p-2 text-base-300 dark:text-neutral">
                        {Object.keys(groupedToolEvents).map((tool) => (
                          <MessageEvents key={tool} events={groupedToolEvents[tool] || []} message={message} />
                        ))}
                      </div>
                    </Collapse>
                  </div>
                  {otherEvents.map((event) => (
                    <MessageEvent key={`${event.data}-${event.data_type}`} event={event} message={message} />
                  ))}
                  <LLMResponse text={message.content} messageId={message.id} conversationId={conversationId} />
                  {message.status === "DONE" &&
                    showFeedback &&
                    (isRecentMessage ? (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5 }}
                      >
                        <FeedbackView
                          feedback={message.feedback}
                          conversationId={conversationId}
                          messageId={message.id}
                          user={session?.user.name}
                        />
                      </motion.div>
                    ) : (
                      <FeedbackView
                        feedback={message.feedback}
                        conversationId={conversationId}
                        messageId={message.id}
                        user={session?.user.name}
                      />
                    ))}
                </div>
                {appendixEvents.length > 0 && (
                  <div className="mt-1 flex w-full flex-col items-center justify-start space-y-1 text-base-300 dark:text-base-300">
                    {appendixEvents.map((data) => (
                      <ToolAppendixRenderer
                        key={data.value}
                        data={data}
                        message={message}
                        isLatestMessage={isLatestMessage}
                        conversationId={conversationId}
                      />
                    ))}
                  </div>
                )}
                <span className="self-end pr-1 pt-1 text-sm text-gray-400">
                  {dayjs(message.createdAt).format("lll")}
                </span>
              </div>
              <div className="invisible group-hover:visible">
                <Dropdown
                  tigger={
                    <button className="ml-1 mt-2 flex h-6 w-6 shrink-0 items-center justify-center text-gray-900 hover:text-gray-900">
                      <Icon.IoMdMore className="h-auto w-5 text-base-300 dark:!text-neutral" />
                    </button>
                  }
                >
                  <div className="flex flex-col items-start justify-start rounded-lg bg-base-100 p-1">
                    <DropdownItem
                      className="flex w-full cursor-pointer flex-row items-center justify-start rounded-lg p-1 px-2 hover:bg-neutral dark:hover:bg-accent"
                      onClick={copyMessage}
                    >
                      <Icon.BiClipboard className="mr-2 h-auto w-4 opacity-70" />
                      Copy
                    </DropdownItem>
                    <DropdownItem
                      className="flex w-full cursor-pointer flex-row items-center justify-start rounded-lg p-1 px-2 hover:bg-neutral dark:hover:bg-accent"
                      onClick={() => deleteMessage(message)}
                    >
                      <Icon.BiTrash className="mr-2 h-auto w-4 opacity-70" />
                      Delete
                    </DropdownItem>
                  </div>
                </Dropdown>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}

export default MessageView
