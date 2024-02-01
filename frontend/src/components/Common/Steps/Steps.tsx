import { Tooltip } from "../Tooltip/Tooltip"

interface StepsProps {
  activeStepIndex: number
  steps: { label: string; description?: string }[]
  onStepClick: (step: number) => void
}

export const Steps = ({ steps, activeStepIndex, onStepClick }: StepsProps) => {
  const getDataContent = (stepIndex: number) => {
    if (stepIndex < activeStepIndex) {
      return "✓"
    }

    return stepIndex + 1
  }

  const getStepColor = (stepIndex: number) => {
    if (stepIndex <= activeStepIndex) {
      return "after:!bg-accent after:!text-neutral"
    }

    return "after:!bg-base-100"
  }

  return (
    <ul className="daisysteps daisysteps-horizontal h-full w-full overflow-visible lg:daisysteps-vertical lg:w-auto">
      {steps?.map((step, index) => {
        const positionClasses =
          index === 0
            ? "daisytooltip-right"
            : index === steps.length - 1
              ? "daisytooltip-left lg:daisytooltip-right"
              : "daisytooltip-bottom lg:daisytooltip-right"

        return (
          <li
            key={step.label}
            data-content={getDataContent(index)}
            className={`daisystep ${getStepColor(
              index
            )} gap-cxs before:!h-c2xs before:min-h-0 before:!w-c2xs before:!min-w-full before:!bg-base-100 after:cursor-pointer lg:before:!h-full lg:before:!w-c2xs lg:before:!min-w-0`}
            onClick={() => onStepClick(index)}
          >
            {step?.description ? (
              <Tooltip content={step.description} position={positionClasses}>
                <span className="cursor-pointer">
                  <div className="daisyindicator">
                    <span className="daisyindicator-item">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        className="h-3 w-3 shrink-0 stroke-current"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        ></path>
                      </svg>
                    </span>
                    <div className="grid place-items-center">{step.label}</div>
                  </div>
                </span>
              </Tooltip>
            ) : (
              <span>{step.label}</span>
            )}
          </li>
        )
      })}
    </ul>
  )
}
