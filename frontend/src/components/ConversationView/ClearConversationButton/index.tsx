import { Modal } from "~/components/Common"
import Icon from "~/components/CustomIcons/Icon"
import { useConversationStore, useMessageStore } from "~/stores"
import ClearConversationConfirmModal from "./ClearConversationConfirmModal"

const ClearConversationButton = () => {
  const conversationStore = useConversationStore()
  const messageStore = useMessageStore()
  const messageList = messageStore.messageList.filter(
    (message) => message.conversationId === conversationStore.currentConversationId
  )

  const getConversationClearModalId = () => "clear-conversation-modal"

  return (
    <>
      <button
        className="daisybtn glass hover:daisybtn-error"
        disabled={messageList.length === 0}
        onClick={() => Modal.openModal(getConversationClearModalId())}
      >
        <Icon.BiTrash className="h-auto w-6" />
      </button>

      {<ClearConversationConfirmModal getConversationClearModalId={getConversationClearModalId} />}
    </>
  )
}

export default ClearConversationButton
