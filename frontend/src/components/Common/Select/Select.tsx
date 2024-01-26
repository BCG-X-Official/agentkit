export interface SelectV2Props<T> {
  label: string | JSX.Element
  optionsList?: { key: string; value: T; label: string }[]
  value?: T
  onChange: (value: T, options?: HTMLOptionsCollection, index?: number) => void
  disabled?: boolean
}

export const Select = <T extends string | number | readonly string[] | undefined>({
  label,
  optionsList,
  value,
  onChange,
  ...rest
}: SelectV2Props<T>) => (
  <div className="daisyform-control flex w-full flex-col">
    <label className="daisylabel font-bold">
      <h3 className="daisylabel-text">{label}</h3>
    </label>
    <select
      className="daisyselect daisyselect-bordered daisyselect-sm bg-neutral !text-fluid-csm lg:daisyselect-md disabled:!bg-base-100 dark:bg-base-200"
      value={value}
      onChange={(e) => onChange?.(e?.target?.value as unknown as T, e?.target?.options, e?.target?.selectedIndex)}
      {...rest}
    >
      {optionsList?.map(({ key, value, label }) => {
        return (
          <option key={key} value={value}>
            {label}
          </option>
        )
      }) ?? []}
    </select>
  </div>
)
