"use client"

import { head } from "lodash-es"
import DataTable from "react-data-table-component"
import Icon from "~/components/CustomIcons/Icon"

interface Props {
  rawResults: Record<string, any>[]
}

const getWidth = (rawResult: Record<string, any>, key: string) => {
  const value = rawResult[key]
  const hasWidth = typeof value === "string"
  return hasWidth && value.length <= 100 ? "25em" : undefined
}

const DataTableView = (props: Props) => {
  const { rawResults } = props
  const columns = Object.keys(head(rawResults) || {}).map((key) => {
    return {
      name: key,
      sortable: true,
      selector: (row: any) => row[key],
      wrap: true,
      maxWidth: getWidth(head(rawResults) || {}, key),
      padding: "0.5em",
      className: "dark:border-zinc-700",
    }
  })

  return rawResults.length === 0 ? (
    <div className="flex w-full flex-col items-center justify-center py-6 pt-10">
      <Icon.BsBoxArrowDown className="h-auto w-7 opacity-70" />
      <span className="mt-2 font-mono text-sm text-gray-500">No data returned</span>
    </div>
  ) : (
    <DataTable
      className="w-full !rounded-lg border dark:border-zinc-700"
      columns={columns}
      data={rawResults}
      fixedHeader
      pagination
      paginationPerPage={5}
      paginationRowsPerPageOptions={[5, 10, 25, 50, 100]}
      responsive
    />
  )
}

export default DataTableView
