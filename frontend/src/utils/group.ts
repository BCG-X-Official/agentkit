import { get } from "lodash-es"

export const groupBy = (array: any[], key: string, defaultGroup: string = "default") => {
  return array.reduce((result, currentValue) => {
    const result_key = get(currentValue, key, defaultGroup)
    ;(result[result_key] = result[result_key] || []).push(currentValue)
    return result
  }, {})
}
