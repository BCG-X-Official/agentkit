import Image from "next/image"
import { signOut } from "next-auth/react"
import { useTheme } from "next-themes"
import { useState } from "react"

import { Accordion, Drawer, Dropdown, DropdownItem, Modal, SettingsModal } from "~/components/Common"
import Icon from "~/components/CustomIcons/Icon"

import { useConversationStore } from "~/stores"
import { type Conversation } from "~/types"

import { APPLICATION_TITLE, getMainLogoSrc, LOGO_SRC } from "~/utils"

import { CONVERSATION_SIDEBAR_SELECTORS } from "./ConversationSidebar.selectors"
import UpdateConversationModal from "./UpdateConversationModal"

const ConversationSidebar = () => {
  const { resolvedTheme } = useTheme()
  const conversationStore = useConversationStore()

  const [updateConversationModalContext, setUpdateConversationModalContext] = useState<Conversation>()
  const conversationList = conversationStore.conversationList

  const handleCreateConversation = () => {
    conversationStore.createConversation()
  }

  const handleConversationSelect = (conversation: Conversation) => {
    conversationStore.setCurrentConversationId(conversation.id)
  }

  const getUpdateConversationModalId = () => "update-conversation-modal"

  const handleEditConversation = (conversation: Conversation) => {
    setUpdateConversationModalContext(conversation)

    Modal.openModal(getUpdateConversationModalId())
  }

  const handleDeleteConversation = (conversation: Conversation) => {
    conversationStore.clearConversation((item: Conversation) => item.id !== conversation.id)
    if (conversationStore.currentConversationId === conversation.id) {
      conversationStore.setCurrentConversationId(undefined)
    }
  }

  const getSettingsModalId = () => "conversation-sidebar-settings-modal"

  return (
    <>
      <Drawer
        pushPageContent={true}
        contentWrapperClasses="w-full max-w-[220px]"
        colapsedHeader={(toggle) => (
          <div
            className="my-clg flex h-full w-full grow flex-col items-center justify-between gap-clg"
            data-cy={CONVERSATION_SIDEBAR_SELECTORS.collapsedSidebarWrapper}
          >
            <Image src={LOGO_SRC} width={40} height={40} alt={APPLICATION_TITLE} />

            <div
              className="flex h-full max-h-[calc(96%-60px)] w-full flex-col
            items-center gap-csm overflow-auto px-c2xs"
            >
              <Accordion
                forceAccordionItemsToggle={true}
                accordionID="conversation-list"
                iconPosition="center"
                items={[
                  {
                    key: "conversation-list",
                    content: (
                      <div
                        className="flex flex-col gap-csm"
                        data-cy={CONVERSATION_SIDEBAR_SELECTORS.collapsedSidebarChatList}
                      >
                        {conversationList.map((conversation: Conversation) => (
                          <div
                            key={conversation.id}
                            className={`group group flex w-full cursor-pointer
                     flex-row justify-center rounded-lg border border-transparent p-0 py-csm hover:bg-accent dark:hover:bg-accent ${
                       conversation.id === conversationStore.currentConversationId
                         ? "border-gray-200 bg-accent font-medium text-neutral dark:bg-accent"
                         : "dark:text-gray-300"
                     }`}
                            onClick={() => handleConversationSelect(conversation)}
                            data-cy={CONVERSATION_SIDEBAR_SELECTORS.collapsedChatListItem}
                          >
                            {conversation.id === conversationStore.currentConversationId ? (
                              <Icon.IoChatbubble className="h-auto w-5 shrink-0" />
                            ) : (
                              <Icon.IoChatbubbleOutline className="h-auto w-5 shrink-0 opacity-80" />
                            )}
                          </div>
                        ))}
                      </div>
                    ),
                  },
                ]}
              />

              <button
                className="daisybtn daisybtn-square glass !w-full capitalize hover:daisybtn-accent"
                onClick={handleCreateConversation}
                data-cy={CONVERSATION_SIDEBAR_SELECTORS.collapsedAddChatButton}
              >
                <Icon.AiOutlinePlus className="text-fluid-cmd" />
              </button>
            </div>

            <div className="w-full">
              <div className="daisydivider" />

              <button
                className="group group daisybtn glass daisybtn-md relative bottom-0 flex w-full justify-center px-csm"
                onClick={() => toggle()}
                data-cy={CONVERSATION_SIDEBAR_SELECTORS.expandSidebarButton}
              >
                <Icon.BiArrowFromLeft className="!text-fluid-cmd hover:!scale-110 hover:!opacity-80 group-hover:!text-neutral" />
              </button>
            </div>
          </div>
        )}
        expandedHeader={
          <div className="m-0 flex w-full justify-center">
            <Image src={getMainLogoSrc(resolvedTheme)} alt={APPLICATION_TITLE} width={200} height={83} />
          </div>
        }
        footer={(toggle) => (
          <div className="flex w-full flex-col justify-center">
            <div className="daisydivider !m-0 py-cmd" />

            <div className="flex w-full justify-center">
              <div className="flex w-full flex-col gap-cmd py-cmd">
                <button className="group daisybtn glass hover:daisybtn-error" onClick={() => signOut()}>
                  <Icon.IoLogOutOutline className="!text-fluid-cmd text-base-200 group-hover:!text-neutral dark:!text-neutral" />
                </button>

                <button
                  className="group daisybtn glass hover:daisybtn-secondary"
                  onClick={() => Modal.openModal(getSettingsModalId())}
                  data-cy={CONVERSATION_SIDEBAR_SELECTORS.collapseSidebarButton}
                >
                  <Icon.FiSettings className="!text-fluid-cmd text-base-200 group-hover:!text-neutral dark:!text-neutral" />
                </button>
              </div>
            </div>

            <div className="daisydivider" />

            <button
              className="group daisybtn glass daisybtn-md flex w-full justify-center px-csm"
              onClick={() => toggle()}
            >
              <Icon.BiArrowFromRight className="!cursor-pointer !text-fluid-cmd group-hover:!text-neutral" />
            </button>
          </div>
        )}
      >
        <div
          className="my-clg flex w-full grow flex-col gap-clg"
          data-cy={CONVERSATION_SIDEBAR_SELECTORS.expandedSidebarWrapper}
        >
          <Accordion
            forceAccordionItemsToggle={true}
            accordionID="conversation-list"
            items={[
              {
                key: "conversation-list",
                title: <>Conversations</>,
                content: (
                  <div
                    className="flex flex-col gap-csm"
                    data-cy={CONVERSATION_SIDEBAR_SELECTORS.expandedSidebarChatList}
                  >
                    {conversationList.map((conversation: Conversation) => (
                      <div
                        key={conversation.id}
                        className={`group group flex w-full cursor-pointer
                     flex-row justify-center rounded-lg border border-transparent px-cxs py-csm hover:bg-accent dark:hover:bg-accent ${
                       conversation.id === conversationStore.currentConversationId
                         ? "border-gray-200 bg-accent font-medium text-neutral dark:bg-accent"
                         : "dark:text-gray-300"
                     }`}
                        onClick={() => handleConversationSelect(conversation)}
                        data-cy={CONVERSATION_SIDEBAR_SELECTORS.expandedChatListItem}
                      >
                        {conversation.id === conversationStore.currentConversationId ? (
                          <Icon.IoChatbubble className="mr-1.5 h-auto w-5 shrink-0" />
                        ) : (
                          <Icon.IoChatbubbleOutline className="mr-1.5 h-auto w-5 shrink-0 opacity-80" />
                        )}

                        <span
                          className={`max-w-full grow truncate break-all group-hover:text-neutral ${
                            conversation.id === conversationStore.currentConversationId ? "!text-neutral" : ""
                          }`}
                        >
                          {conversation.title || "SmartSmileGuide"}
                        </span>

                        <Dropdown
                          tigger={
                            <button
                              className="invisible ml-2 flex h-auto w-4 shrink-0 items-center justify-center text-gray-400 hover:text-gray-500 group-hover:visible"
                              data-cy={CONVERSATION_SIDEBAR_SELECTORS.chatEllipsisButton}
                            >
                              <Icon.FiMoreHorizontal className="h-auto w-full group-hover:text-neutral" />
                            </button>
                          }
                        >
                          <div className="flex flex-col items-start justify-start rounded-lg bg-white p-1 shadow-lg dark:bg-zinc-900">
                            <DropdownItem
                              className="flex w-full cursor-pointer flex-row items-center justify-start rounded-lg p-1 px-2 hover:bg-neutral dark:hover:bg-accent"
                              onClick={() => handleEditConversation(conversation)}
                              data-cy={CONVERSATION_SIDEBAR_SELECTORS.editChatButton}
                            >
                              <Icon.FiEdit3 className="mr-2 h-auto w-4 opacity-70" />
                              Edit
                            </DropdownItem>
                            <DropdownItem
                              className="flex w-full cursor-pointer flex-row items-center justify-start rounded-lg p-1 px-2 hover:bg-neutral dark:hover:bg-accent"
                              onClick={() => handleDeleteConversation(conversation)}
                              data-cy={CONVERSATION_SIDEBAR_SELECTORS.deleteChatButton}
                            >
                              <Icon.IoTrash className="mr-2 h-auto w-4 opacity-70" />
                              Delete
                            </DropdownItem>
                          </div>
                        </Dropdown>
                      </div>
                    ))}
                  </div>
                ),
              },
            ]}
          />

          <button
            className="daisybtn daisybtn-accent capitalize text-neutral"
            onClick={handleCreateConversation}
            data-cy={CONVERSATION_SIDEBAR_SELECTORS.expandedAddChatButton}
          >
            <Icon.AiOutlinePlus className="text-fluid-cmd" />
            <>New chat</>
          </button>
        </div>
      </Drawer>

      {updateConversationModalContext && (
        <UpdateConversationModal
          getUpdateConversationModalId={getUpdateConversationModalId}
          conversation={updateConversationModalContext}
        />
      )}

      {<SettingsModal getSettingsModalId={getSettingsModalId} />}
    </>
  )
}

export default ConversationSidebar
