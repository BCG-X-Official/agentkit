import { ToolActionRenderer } from "~/components/ToolActionRenderer"
import { type Message, type MessageEvent as MessageEventT } from "~/types"
import { LLMResponse } from "./LLMResponse"

interface Props {
  message: Message
  event: MessageEventT
}

export const MessageEvent = (props: Props) => {
  const { message, event } = props

  switch (event.data_type) {
    case "action":
      return <ToolActionRenderer text={event.data} metadata={event.metadata} />
    case "llm":
      return <LLMResponse text={event.data} messageId={message.id} conversationId={message.conversationId} />
    case "signal":
      return null
    case "appendix":
      return null
    default:
      return <div>{event.data}</div>
  }
}
