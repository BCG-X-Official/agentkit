export enum TooltipSize {
  Small = "small",
  Normal = "normal",
  Combined = "combined",
}

export interface TooltipProps {
  size?: TooltipSize
  content?: string
  position?: string
  children: JSX.Element | JSX.Element[]
  wrapperClasses?: string
}

export const Tooltip = ({
  content,
  position = "daisytooltip-bottom",
  size = TooltipSize.Normal,
  wrapperClasses = "",
  children,
}: TooltipProps) => {
  const getSizeClasses = () => {
    if (size === TooltipSize.Small) {
      return "before:!text-csm before:!p-csm"
    }

    if (size === TooltipSize.Normal) {
      return "before:!text-fluid-csm before:!p-csm"
    }

    return "before:!text-csm before:!p-csm lg:before:!text-fluid-csm"
  }

  return (
    <div
      className={`daisytooltip flex ${position} ${getSizeClasses()} !mx-0 !my-auto before:!z-10 before:!rounded-lg before:text-left before:!font-normal before:text-opacity-90 before:hover:!bg-base-300 before:hover:!text-neutral ${wrapperClasses}`}
      data-tip={content}
    >
      {children}
    </div>
  )
}
