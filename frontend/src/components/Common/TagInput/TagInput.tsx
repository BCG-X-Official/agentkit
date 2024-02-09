import { useState } from "react"

import { createTag, type CreateTagType } from "./TagInput.types"

interface TagInputProps {
  tags: CreateTagType[]
  setTags: (tags: CreateTagType[]) => void
}

export const TagInput = ({ tags, setTags }: TagInputProps) => {
  const [inputValue, setInputValue] = useState("")

  const handleInputChange = (e: any) => {
    setInputValue(e?.target?.value)
  }

  const handleKeyDown = (e: any) => {
    if ((e?.key === "Enter" || e?.key === "Tab") && inputValue?.trim() !== "") {
      e?.preventDefault()
      setTags([...tags, createTag({ value: inputValue?.trim() })])
      setInputValue("")
    } else if (e?.key === "Backspace" && inputValue === "") {
      setTags(tags?.slice(0, -1))
    }
  }

  const handleRemoveTag = (tag: CreateTagType) => {
    setTags(tags?.filter((t) => t.id !== tag.id))
  }

  return (
    <div className="flex w-full flex-wrap items-center gap-cxs rounded bg-transparent">
      {tags?.map((tag) => (
        <div
          key={tag.id}
          className={`flex items-center rounded-md px-2 py-1 text-[15px] !text-neutral`}
          style={{ backgroundColor: tag.color }}
        >
          <span className="!text-neutral">{tag.value}</span>
          <button className="ml-2 p-1 text-xs" onClick={() => handleRemoveTag(tag)}>
            x
          </button>
        </div>
      )) ?? []}
      <input
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder="Add filter..."
        className="daisyinput daisyinput-bordered daisyinput-md w-full flex-1 bg-neutral outline-none disabled:!bg-base-100 dark:bg-base-200"
      />
    </div>
  )
}
