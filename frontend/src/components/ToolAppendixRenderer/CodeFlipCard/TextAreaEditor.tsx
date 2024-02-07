import { useState } from "react"

interface Props {
  code: string
}

const TextAreaEditor = (props: Props) => {
  let { code } = props
  const [value, setValue] = useState(code)
  // submit code to backend
  const handleSubmit = () => {
    //TODO - submit code to backend
  }
  return (
    <>
      <textarea
        value={value}
        readOnly={true}
        onChange={(e) => setValue(e.target.value)}
        className="h-96 w-full rounded-md bg-neutral p-2 font-mono text-gray-900 dark:bg-gray-900 dark:text-gray-100"
        style={{ resize: "vertical" }}
      />
      <button
        onClick={handleSubmit}
        className="mt-2 h-10 w-64 rounded-md bg-green-500 text-white"
        disabled={true}
        // disable color when disabled
        style={{ backgroundColor: "#4CAF50", opacity: 0.5 }}
      >
        Save
      </button>
    </>
  )
}

export default TextAreaEditor
