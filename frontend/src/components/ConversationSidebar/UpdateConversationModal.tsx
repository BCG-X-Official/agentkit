import { useState } from "react"

import { toast } from "react-hot-toast"

import { Modal, TextField } from "~/components/Common"
import { useConversationStore } from "~/stores"
import { type Conversation } from "~/types"

import { CONVERSATION_SIDEBAR_SELECTORS } from "./ConversationSidebar.selectors"

interface Props {
  conversation: Conversation
  getUpdateConversationModalId: (id?: string) => string
}

const UpdateConversationModal = (props: Props) => {
  const { conversation, getUpdateConversationModalId } = props
  const conversationStore = useConversationStore()
  const [title, setTitle] = useState(conversation?.title)
  const allowSave = title !== ""

  const handleSaveEdit = () => {
    const formatedTitle = title.trim()
    if (formatedTitle === "") {
      return
    }

    conversationStore.updateConversation(conversation.id, {
      title: formatedTitle,
    })
    toast.success("Conversation updated")
    Modal.closeModal(modalId)
  }

  const modalId = getUpdateConversationModalId()

  return (
    <Modal.Component
      uniqueModalId={modalId}
      actionButtons={
        <div className="flex w-64 flex-row items-center justify-end gap-csm">
          <button
            className="daisybtn daisybtn-primary daisybtn-sm font-normal capitalize text-neutral lg:daisybtn-md hover:opacity-80"
            disabled={!allowSave}
            onClick={handleSaveEdit}
            data-cy={CONVERSATION_SIDEBAR_SELECTORS.saveChatButton}
          >
            Save
          </button>
          <button
            className="daisybtn glass daisybtn-sm font-normal capitalize lg:daisybtn-md hover:text-neutral"
            onClick={() => {
              Modal.closeModal(modalId)
            }}
          >
            Close
          </button>
        </div>
      }
    >
      <div
        className="flex flex-col items-center justify-center rounded-lg bg-transparent px-cmd py-cxl dark:bg-base-100"
        data-cy={CONVERSATION_SIDEBAR_SELECTORS.updateChatContentWrapper}
      >
        <h3 className="m-0 p-0 !text-fluid-cmd font-bold">Update chat</h3>
        <div className="mt-2 flex w-full flex-col items-start justify-start">
          <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Title</label>
          <TextField
            placeholder={"Chat title"}
            value={title}
            onChange={(value) => setTitle(value)}
            data-cy={CONVERSATION_SIDEBAR_SELECTORS.updateChatTextField}
          />
        </div>
      </div>
    </Modal.Component>
  )
}

export default UpdateConversationModal
