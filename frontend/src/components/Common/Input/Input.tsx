import { forwardRef, type Ref } from "react"

export interface InputProps {
  type?: string
  onKeyDown?: (value: any) => void
  label?: string | JSX.Element
  value?: any
  onChange: (value: any) => void
  placeholder?: string
  disabled?: boolean
  classNames?: string
  autoFocus?: boolean
}

export const Input = forwardRef(function Input(
  { label, value, onChange, onKeyDown, placeholder, ...rest }: InputProps,
  ref: Ref<any>
) {
  return (
    <div className="daisyform-control flex w-full flex-col">
      {label && (
        <label className="daisylabel font-bold">
          <h3 className="daisylabel-text !text-fluid-cmd">{label}</h3>
        </label>
      )}
      <input
        value={value}
        onChange={(e) => onChange?.(e?.target?.value as unknown as any)}
        onKeyDown={(e: any) => onKeyDown?.(e?.target?.value as unknown as any)}
        {...rest}
        type="text"
        placeholder={placeholder}
        className="daisyinput daisyinput-bordered daisyinput-sm w-full bg-neutral lg:daisyinput-md disabled:!bg-base-100 dark:bg-base-200"
        ref={ref}
      />
    </div>
  )
})
