import { type ExecutionResult } from "~/api-client"

export const getMessageFromExecutionResult = (result: ExecutionResult): string => {
  if (result.error) {
    return result.error
  }
  if (result.affectedRows) {
    return `${result.affectedRows} rows affected.`
  }
  return ""
}

export const checkStatementIsSelect = (statement: string) => {
  return statement.toUpperCase().trim().startsWith("SELECT") || statement.toUpperCase().trim().startsWith("WITH")
}

export const filterNonFlattenedObjectFields = (rest: Record<string, any>) => {
  // Filters out any non-flattened fields. If needed, adjust.
  return Object.keys(rest).reduce(
    (acc: any, key: any) => (typeof rest[key] === "object" ? acc : { ...acc, [key]: rest[key] }),
    {}
  )
}
