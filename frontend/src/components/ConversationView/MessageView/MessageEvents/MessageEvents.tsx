import { get } from "lodash-es"

import { StreamingDataTypeEnum, StreamingSignalsEnum } from "~/api-client"

import ThreeDotsLoader from "~/components/CustomIcons/ThreeDotsLoader"
import { type Message, type MessageEvent as MessageEventT } from "~/types"
import { MessageEvent } from "./MessageEvent"

interface Props {
  message: Message
  events: MessageEventT[]
}

export const MessageEvents = (props: Props) => {
  const { message, events } = props

  const isToolAction = events.some((event) => event.data_type === StreamingDataTypeEnum.ACTION && event.metadata?.tool)
  const actionHasEnded = events.some(
    (event) => event.data_type === StreamingDataTypeEnum.SIGNAL && event.data === StreamingSignalsEnum.TOOL_END
  )
  const messageHasEnded = message.status !== "LOADING"

  return (
    <div>
      {events
        .sort((e1, e2) => get(e1, "step", 0) - get(e2, "step", 0))
        .map((event, index) => (
          <MessageEvent key={`${event.data}-${event.data_type}-${index}`} event={event} message={message} />
        ))}
      {isToolAction && !actionHasEnded && !messageHasEnded && (
        <div className="ml-5">
          <ThreeDotsLoader />
        </div>
      )}
    </div>
  )
}
