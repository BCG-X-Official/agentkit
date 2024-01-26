import { useEffect, useState } from "react"

import { toast } from "react-hot-toast"
import TextareaAutosize from "react-textarea-autosize"

import { type ExecutionResult, SqlService } from "~/api-client"
import { Drawer, Tooltip } from "~/components/Common"
import Icon from "~/components/CustomIcons/Icon"
import { useQueryStore } from "~/stores"
import { checkStatementIsSelect, getMessageFromExecutionResult } from "~/utils"

import DataTableView from "./DataTableView"
import ExecutionWarningBanner from "./ExecutionWarningBanner"
import NotificationView from "./NotificationView"

const SideDrawer = () => {
  const queryStore = useQueryStore()
  const [executionResult, setExecutionResult] = useState<ExecutionResult | undefined>(undefined)
  const [statement, setStatement] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)
  const context = queryStore.context
  const executionMessage = executionResult ? getMessageFromExecutionResult(executionResult) : ""
  const showExecutionWarningBanner = statement.trim() && !checkStatementIsSelect(statement)
  const showDrawer = queryStore.getState().showDrawer

  useEffect(() => {
    if (!showDrawer) {
      return
    }

    const statement = context?.statement || ""
    setStatement(statement)
    if (statement !== "" && checkStatementIsSelect(statement)) {
      executeStatement(statement)
    }
    setExecutionResult(undefined)
  }, [context, showDrawer])

  const executeStatement = async (statement: string) => {
    if (!statement) {
      toast.error("Please enter a statement.")
      return
    }

    if (!context) {
      toast.error("No execution context found.")
      setIsLoading(false)
      setExecutionResult(undefined)
      return
    }

    setIsLoading(true)
    setExecutionResult(undefined)
    try {
      const result = await SqlService.executeSqlApiV1SqlExecuteGet(statement)
      if (result.data) {
        setExecutionResult(result.data)
        queryStore.setQueryCache(statement, result.data.rawResult, context.messageId, context.conversationId)
      } else if (!result.data && result.message) {
        setExecutionResult({
          rawResult: [],
          error: result.message,
        })
      }
    } catch (error) {
      console.error(error)
      toast.error("Failed to execute statement")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Drawer
      isOpen={showDrawer}
      side="right"
      contentWrapperClasses="w-full md:max-w-[400px] xl:max-w-[600px]"
      footer={(toggle) => (
        <div className="flex w-full flex-col justify-center">
          <button
            className="group daisybtn glass daisybtn-md flex w-full justify-center px-csm"
            onClick={() => toggle()}
          >
            <Icon.BiArrowFromLeft className="!cursor-pointer !text-fluid-cmd group-hover:!text-neutral" />
          </button>
        </div>
      )}
      onToggle={(isOpen) => queryStore.toggleDrawer(isOpen)}
    >
      <div className="flex w-screen max-w-full flex-col items-start justify-start p-4 sm:w-[calc(60vw)] lg:w-[calc(50vw)] 2xl:w-[calc(40vw)] dark:text-gray-300">
        <h2 className="pb-cmd text-fluid-cmd font-bold">Execute SQL</h2>
        <>
          <div className="mt-4 flex w-full flex-row items-center justify-start">
            <Icon.GoDatabase className="h-auto w-6 align-middle" />
            <h5 className="text-1xl ml-2 align-middle font-bold">Database</h5>
          </div>
          {showExecutionWarningBanner && <ExecutionWarningBanner className="mt-4 rounded-lg" />}
          <div className="mt-4 flex h-auto w-full flex-row items-end justify-between text-clip rounded-lg border bg-neutral px-2 dark:border-zinc-700 dark:bg-base-300">
            <TextareaAutosize
              className="hide-scrollbar h-full w-full resize-none whitespace-pre-wrap break-all border-none bg-transparent py-2 pl-2 font-mono text-sm leading-6 outline-none"
              value={statement}
              rows={1}
              minRows={1}
              maxRows={5}
              placeholder="Enter your SQL statement here..."
              onChange={(e) => setStatement(e.target.value)}
            />
            <Tooltip content={"Execute"} position="daisytooltip-top">
              <button
                className="w-6 -translate-y-2 cursor-pointer rounded-md bg-accent p-1 text-gray-50 opacity-90 hover:opacity-100 hover:shadow disabled:cursor-not-allowed disabled:opacity-60"
                onClick={() => executeStatement(statement)}
              >
                <Icon.IoPlay className="h-auto w-full" />
              </button>
            </Tooltip>
          </div>
          <div className="mt-4 flex w-full flex-col items-start justify-start">
            {isLoading ? (
              <div className="flex w-full flex-col items-center justify-center py-6 pt-10">
                <Icon.BiLoaderAlt className="h-auto w-7 animate-spin opacity-70" />
                <span className="mt-2 font-mono text-sm text-gray-500">{"Executing query..."}</span>
              </div>
            ) : (
              <>
                {executionResult ? (
                  executionMessage ? (
                    <NotificationView message={executionMessage} style={executionResult?.error ? "error" : "info"} />
                  ) : (
                    <DataTableView rawResults={executionResult?.rawResult || []} />
                  )
                ) : (
                  <></>
                )}
              </>
            )}
          </div>
        </>
      </div>
    </Drawer>
  )
}

export default SideDrawer
