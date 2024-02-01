import { useEffect, useState } from "react"

import Icon from "~/components/CustomIcons/Icon"

import { useSettingStore } from "~/stores"
import { Input } from "../Input/Input"
import { Modal } from "../Modal/Modal"

interface Props {
  getSettingsModalId: (id?: string) => string
}

export const SettingsModal = (props: Props) => {
  const { getSettingsModalId } = props
  const settingsStore = useSettingStore()

  const [openaiApiKey, setOpenaiApiKey] = useState<string>("")
  const [openaiOrgId, setOpenaiOrgId] = useState<string>("")
  const [favoriteArtist, setFavoriteArtist] = useState<string>(settingsStore.setting.data["favorite_artist"])

  useEffect(() => {
    const apiKey = localStorage.getItem("openaiApiKey")
    const orgId = localStorage.getItem("openaiOrgId") //

    if (apiKey) {
      setOpenaiApiKey(apiKey)
    }

    if (orgId) {
      setOpenaiOrgId(orgId)
    }
  }, [])

  const saveSettings = () => {
    localStorage.setItem("openaiApiKey", openaiApiKey)
    settingsStore.setSetting({
      data: {
        favorite_artist: favoriteArtist,
        api_key: openaiApiKey,
      },
    })
    Modal.closeModal(modalId)
  }

  const modalId = getSettingsModalId()

  return (
    <Modal.Component
      uniqueModalId={modalId}
      actionButtons={
        <div className="flex w-64 flex-row items-center justify-end gap-csm">
          <button
            className="daisybtn daisybtn-secondary daisybtn-sm  font-normal capitalize lg:daisybtn-md"
            onClick={() => saveSettings()}
          >
            <Icon.FiSave className="mr-1 h-auto w-5" />
            Save
          </button>
          <button
            className="daisybtn glass daisybtn-sm font-normal capitalize lg:daisybtn-md hover:text-neutral"
            onClick={() => Modal.closeModal(modalId)}
          >
            <Icon.FiX className="mr-1 h-auto w-5" />
            Cancel
          </button>
        </div>
      }
    >
      <div className="flex flex-col items-center justify-center rounded-lg bg-transparent px-cmd py-cxl dark:bg-base-100">
        <h3 className="m-0 p-0 !text-fluid-cmd font-bold">Settings</h3>
        <div className="daisydivider" />
        <div className="flex h-full w-full flex-col gap-cmd">
          <Input type="text" label="OpenAI API Key" value={openaiApiKey} onChange={(value) => setOpenaiApiKey(value)} />
          <Input type="text" label="OpenAI Org ID" value={openaiOrgId} onChange={(value) => setOpenaiOrgId(value)} />
          <Input
            type="text"
            label="Favorite artist"
            value={favoriteArtist}
            onChange={(e) => setFavoriteArtist(e.target.value)}
          />
        </div>
      </div>
    </Modal.Component>
  )
}
