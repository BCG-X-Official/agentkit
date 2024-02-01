"use client"

import { useLocalStorageValue } from "@react-hookz/web"
import Icon from "~/components/CustomIcons/Icon"

interface Props {
  className?: string
  alwaysShow?: boolean
}

export const TopWarningBanner = (props: Props) => {
  const { className, alwaysShow } = props
  const { value: hideBanner, set: setHideBanner } = useLocalStorageValue("hide-local-storage-banner", {
    defaultValue: false,
    initializeWithValue: false,
  })
  const hide = hideBanner === undefined ? false : hideBanner

  return (
    <div
      className={`${!alwaysShow && hide && "!hidden"} ${
        className || ""
      } relative flex w-full flex-row items-center justify-start bg-accent px-4 py-1 sm:justify-center`}
    >
      <span className="pr-4 text-sm leading-6 !text-white">
        <Icon.IoInformationCircleOutline className="-mt-0.5 mr-0.5 inline-block h-5 w-auto opacity-80" />
        Conversations are only stored in your local browser
      </span>
      {!alwaysShow && (
        <button
          className="absolute right-2 opacity-60 hover:opacity-100 sm:right-4"
          onClick={() => setHideBanner(true)}
        >
          <Icon.BiX className="h-auto w-6 !text-white" />
        </button>
      )}
    </div>
  )
}
