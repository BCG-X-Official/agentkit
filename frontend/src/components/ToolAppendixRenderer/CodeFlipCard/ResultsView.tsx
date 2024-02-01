import Image from "next/image"
import { useMemo } from "react"
import { getMessageFromExecutionResult } from "@/utils"
import { type ExecutionResult } from "~/api-client"
import { SUPPORTED_SYNTAX_LANGUAGES } from "~/types"
import JsxDisplay from "./JsxDisplay"
import PlotlyDisplay from "./PlotlyDisplay"
import TextAreaEditor from "./TextAreaEditor"
import DataTableView from "../../CodeView/SideDrawer/DataTableView"
import NotificationView from "../../CodeView/SideDrawer/NotificationView"
import Icon from "../../CustomIcons/Icon"

interface Props {
  executionResult: ExecutionResult | undefined
  isLoading: boolean
  language: string
  code: string
  graph_ref: any
}

const ResultsView = (props: Props) => {
  const { executionResult, isLoading, language, code, graph_ref } = props
  const executionMessage = executionResult ? getMessageFromExecutionResult(executionResult) : ""

  const result = useMemo(() => {
    switch (language) {
      case SUPPORTED_SYNTAX_LANGUAGES.JSX:
        return <JsxDisplay code={code} data={executionResult?.rawResult || []} graph_ref={graph_ref} />
      case SUPPORTED_SYNTAX_LANGUAGES.SQL:
        return <DataTableView rawResults={executionResult?.rawResult || []} />
      case SUPPORTED_SYNTAX_LANGUAGES.CLINGOV_URL:
        return <DataTableView rawResults={executionResult?.rawResult || []} />
      case SUPPORTED_SYNTAX_LANGUAGES.YAML:
      case SUPPORTED_SYNTAX_LANGUAGES.JSON:
        return <TextAreaEditor code={code} />
      case SUPPORTED_SYNTAX_LANGUAGES.PLOTLY:
        return <PlotlyDisplay code={code} />
      case SUPPORTED_SYNTAX_LANGUAGES.IMAGEURL:
        return <Image src={code} width={300} height={200} alt="img" />
      default:
        return <h1>Sorry, this language is not supported yet</h1>
    }
  }, [code, executionResult, isLoading])

  return (
    <div className="flex flex-col items-start justify-start p-4 dark:text-gray-300">
      <div className="mt-4 flex w-full flex-col items-start justify-start">
        {isLoading ? (
          <div className="flex w-full flex-col items-center justify-center py-6 pt-10">
            <Icon.BiLoaderAlt className="h-auto w-7 animate-spin opacity-70" />
            <span className="mt-2 font-mono text-sm text-gray-500">Executing query...</span>
          </div>
        ) : (
          <>
            {executionResult ? (
              executionMessage ? (
                <NotificationView message={executionMessage} style={executionResult?.error ? "error" : "info"} />
              ) : (
                result
              )
            ) : (
              <></>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default ResultsView
