import { get } from "lodash-es"
import Icon from "@/components/CustomIcons/Icon"
import actions from "./actions"

interface Props {
  text: string
  metadata: { [key: string]: string }
}

export const ToolActionRenderer = (props: Props) => {
  const { text, metadata } = props

  if (!text) return null

  let metadataInfo = null
  const action = (actions as any)[text.toLowerCase()] || {
    icon: () => <Icon.BiQuestionMark className="mb-1 mr-2 h-auto w-6 text-accent" />,
    text: () => text,
  }
  if (metadata && action.getMetadataInfo) {
    metadataInfo = action.getMetadataInfo(metadata)
  }

  const margin = (get(metadata, "step", 0) as number) * 5 * 0.25
  return (
    <div className={`mb-1 flex w-auto`} style={{ marginLeft: `${margin}rem` }}>
      {action.icon(metadata)}
      {action.text(metadata)}
      {metadataInfo && <div className="ml-2 text-accent">{metadataInfo}</div>}
    </div>
  )
}
