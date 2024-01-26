import { forwardRef, type Ref } from "react"

interface TextFieldProps {
  value: any
  onChange: (value: any) => void
  disabled?: boolean
  label?: string
  placeholder?: string
  height?: string
  autoFocus?: boolean
}

export const TextField = forwardRef(function TextField(
  { value, placeholder, label, onChange, height = "h-32", ...rest }: TextFieldProps,
  ref?: Ref<any>
) {
  return (
    <div className="daisyform-control flex w-full flex-col">
      <label className="daisylabel font-bold">
        <h3 className="daisylabel-text">{label}</h3>
      </label>
      <textarea
        className={`daisytextarea daisytextarea-sm bg-neutral lg:daisytextarea-md disabled:!bg-base-100 dark:bg-base-200 ${height} !text-fluid-csm outline !outline-1 outline-offset-2 outline-base-100`}
        placeholder={placeholder ?? ""}
        value={value}
        onChange={(e) => onChange?.(e?.target?.value as unknown as any)}
        {...rest}
        ref={ref}
      />
    </div>
  )
})
