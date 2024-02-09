import { ChatService } from "~/api-client"
import Icon from "~/components/CustomIcons/Icon"
import { useMessageStore } from "~/stores"
import type { Message } from "~/types"

interface Props {
  lastMessage?: Message
}

const CancelMessageButton = (props: Props) => {
  const { lastMessage } = props
  const messageStore = useMessageStore()

  const cancelMessage = () => {
    if (!lastMessage) return

    messageStore.updateMessage(lastMessage.id, {
      status: "CANCELLED",
    })

    if (lastMessage.runId) {
      ChatService.runCancelApiV1ChatRunRunIdCancelGet(lastMessage.runId)
    }
  }

  if (!lastMessage || lastMessage.status !== "LOADING") {
    return null
  }

  return (
    <>
      <button
        className="daisybtn glass hover:daisybtn-error"
        disabled={!lastMessage || lastMessage.status !== "LOADING"}
        onClick={cancelMessage}
      >
        <Icon.MdOutlineCancel className="h-auto w-6" />
      </button>
    </>
  )
}

export default CancelMessageButton
