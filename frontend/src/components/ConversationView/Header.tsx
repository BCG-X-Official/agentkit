import { useEffect } from "react"

import { useConversationStore } from "~/stores"
import { APPLICATION_TITLE } from "~/utils"

import { CONVERSATION_VIEW_SELECTORS } from "./ConversationView.selectors"
import { ThemeSwitch } from "../Common"

const Header = () => {
  const conversationStore = useConversationStore()
  const currentConversationId = conversationStore.currentConversationId
  const title = conversationStore.getConversationById(currentConversationId)?.title || APPLICATION_TITLE

  useEffect(() => {
    document.title = `${title}`
  }, [title])

  return (
    <div
      className="daisynavbar items-center justify-center border-b-[2px] bg-neutral p-csm dark:border-b-base-100 dark:!bg-base-200"
      data-cy={CONVERSATION_VIEW_SELECTORS.topbarWrapper}
    >
      <div className="absolute !right-csm !top-cmd z-[1000]">
        <ThemeSwitch />
      </div>

      <h1 className="text-overflow-ellipsis overflow-hidden p-1 text-center text-fluid-csm font-bold">{title}</h1>
    </div>
  )
}

export default Header
