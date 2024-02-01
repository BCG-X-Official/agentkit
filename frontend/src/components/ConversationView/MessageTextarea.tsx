import { useEffect, useRef, useState } from "react"

import { toast } from "react-hot-toast"
import TextareaAutosize from "react-textarea-autosize"

import { ICreatorRole } from "~/api-client"
import Icon from "~/components/CustomIcons/Icon"
import { useConversationStore, useMessageStore, useUserStore } from "~/stores"
import { generateUUID } from "~/utils"

import { CONVERSATION_VIEW_SELECTORS } from "./ConversationView.selectors"

interface Props {
  disabled?: boolean
  sendMessage: () => Promise<void>
}

const MessageTextarea = (props: Props) => {
  const { disabled, sendMessage } = props
  const userStore = useUserStore()
  const conversationStore = useConversationStore()
  const messageStore = useMessageStore()
  const [value, setValue] = useState<string>("")
  const [isInIME, setIsInIME] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value)
  }

  const handleSend = async () => {
    let conversation = conversationStore.getConversationById(conversationStore.currentConversationId)
    if (!conversation) {
      conversation = conversationStore.createConversation()
    }
    if (!value) {
      toast.error("Please enter a message.")
      return
    }
    if (disabled) {
      return
    }

    messageStore.addMessage({
      id: generateUUID(),
      conversationId: conversation.id,
      creatorId: userStore.currentUser.id,
      creatorRole: ICreatorRole.USER,
      createdAt: Date.now(),
      content: value,
      events: [],
      status: "DONE",
    })
    setValue("")
    textareaRef.current!.value = ""
    await sendMessage()
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey && !isInIME) {
      event.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-auto w-full flex-row items-end justify-between rounded-lg border border-base-100 px-2 py-1">
      <TextareaAutosize
        ref={textareaRef}
        className="hide-scrollbar h-full w-full resize-none border-none bg-transparent p-2 leading-6 outline-none"
        placeholder={"Message the agent"}
        rows={1}
        minRows={1}
        maxRows={5}
        onCompositionStart={() => setIsInIME(true)}
        onCompositionEnd={() => setIsInIME(false)}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        data-cy={CONVERSATION_VIEW_SELECTORS.textInputArea}
      />
      <button
        className="glass w-8 -translate-y-1 cursor-pointer rounded-md p-1 hover:shadow disabled:cursor-not-allowed disabled:opacity-60"
        disabled={disabled}
        onClick={handleSend}
        data-cy={CONVERSATION_VIEW_SELECTORS.sendMessageButton}
      >
        <Icon.IoMdSend className="h-auto w-full text-accent" />
      </button>
    </div>
  )
}

export default MessageTextarea
