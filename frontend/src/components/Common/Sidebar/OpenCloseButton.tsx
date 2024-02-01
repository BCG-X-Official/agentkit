import Icon from "~/components/CustomIcons/Icon"

interface Props {
  onClick: any
  reverseArrows?: boolean
}

export const CloseSidebarButton = ({ onClick, reverseArrows = false }: Props) => {
  const IconComponent = reverseArrows ? Icon.BiArrowFromLeft : Icon.BiArrowFromRight
  return (
    <>
      <button
        className="flex h-10 w-10 flex-row items-center justify-center rounded-full p-1 text-gray-600 hover:bg-accent hover:text-gray-900 dark:text-gray-300 dark:hover:bg-accent dark:hover:text-gray-100"
        onClick={onClick}
      >
        <IconComponent className="h-auto w-6 text-gray-600 dark:text-gray-300" />
      </button>
      <div onClick={onClick} className="absolute left-0 top-0 z-10 h-full w-full bg-black opacity-70 sm:hidden"></div>
    </>
  )
}

export const OpenSidebarButton = ({ onClick, reverseArrows = false }: Props) => {
  const IconComponent = reverseArrows ? Icon.BiArrowFromRight : Icon.BiArrowFromLeft
  return (
    <button
      className="flex h-10 w-10 flex-row items-center justify-center rounded-full p-1 text-gray-600 hover:bg-accent hover:text-gray-900 dark:text-gray-300 dark:hover:bg-accent dark:hover:text-gray-100"
      onClick={onClick}
    >
      <IconComponent className="h-auto w-6 text-gray-600 dark:text-gray-300" />
    </button>
  )
}
