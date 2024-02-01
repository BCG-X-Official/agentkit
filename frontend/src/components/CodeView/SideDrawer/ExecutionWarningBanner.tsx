import Icon from "~/components/CustomIcons/Icon"

interface Props {
  className?: string
}

const ExecutionWarningBanner = (props: Props) => {
  const { className } = props

  return (
    <div
      className={`${
        className || ""
      } relative flex w-full flex-row items-center justify-start bg-yellow-100 px-4 py-2 dark:bg-base-100`}
    >
      <span className="pr-4 text-sm leading-6">
        <Icon.IoInformationCircleOutline className="-mt-0.5 mr-0.5 inline-block h-5 w-auto opacity-80" />
        The statement may be non-SELECT SQL, which will result in a database schema or data change. Double check the
        statement to ensure it is intended.
      </span>
    </div>
  )
}

export default ExecutionWarningBanner
