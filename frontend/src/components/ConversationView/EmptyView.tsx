import Image from "next/image"

import { useTheme } from "next-themes"
import { APPLICATION_TITLE, getMainLogoSrc } from "~/utils"
import { CONVERSATION_VIEW_SELECTORS } from "./ConversationView.selectors"

// examples are used to show some examples to the user.
const examples = [
  "How many artists and songs are there in the database?",
  "What are the names of the customers we have in Paris?",
  "Can you generate a chart which shows the number of unique tracks available per artist? Show me only the top 10 artists by number of tracks.",
]

interface Props {
  className?: string
  sendMessage: () => Promise<void>
}

const EmptyView = (props: Props) => {
  const { className } = props
  const { resolvedTheme } = useTheme()

  return (
    <div
      className={`${className || ""} flex h-full w-full flex-col items-center justify-start text-black dark:text-black`}
      data-cy={CONVERSATION_VIEW_SELECTORS.emptyChatMessageAreaWrapper}
    >
      {/* <GradientTextSVG /> */}
      <div className="mb-8 flex w-96 max-w-full items-center justify-center font-medium leading-loose">
        <div className="max-w-[500px] rounded-lg">
          <Image src={getMainLogoSrc(resolvedTheme)} alt={APPLICATION_TITLE} width="175" height="175" priority />
        </div>
      </div>
      <div className="group mx-auto flex w-full max-w-full flex-row items-start justify-start rounded-lg bg-base-100 p-4">
        <div className="mr-2 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-gray-950">
          <Image src="/logo.png" width="25" height="25" alt="agent" priority />
        </div>
        <div className="mb-4 w-full px-4 py-3">
          <h3 className="font-medium"> Can be used with any set of tools as a general purpose helpful chatbot!</h3>
          <div className="mt-2 text-sm leading-loose text-gray-500 dark:text-gray-500">
            <p>Here are the simple examples for general use cases:</p>
            <ol className="mb-4 list-decimal pl-6">
              {examples.map((example, index) => (
                <li key={index}>
                  <span>{example}</span>
                </li>
              ))}
            </ol>
            <p>It&apos;s that simple!</p>
            <p>
              Remember, you can always refine you requests and ask our chatbot additional questions for a clearer
              understanding of the logic behind the suggested amendments.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmptyView
