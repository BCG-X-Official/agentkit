// @ts-nocheck
/* eslint-disable */
// Library needs to adapt to React 18 typings, open issue: https://github.com/TroyAlford/react-jsx-parser/issues/234
import { first, get } from "lodash-es"

import JsxParser from "react-jsx-parser"
import * as Recharts from "recharts"

import { groupBy } from "~/utils"

interface Props {
  code: string
  data: Record<string, any>[]
  graph_ref: any
}

const ResponsiveWrapper = ({ height, width, data, code, graph_ref, getColors, groupAndMerge, getObjectKeys, func }) => {
  return (
    <JsxParser
      bindings={{
        data: data,
        width: width,
        height: height,
        ref: graph_ref,
        getColors: getColors,
        groupBy: groupBy,
        getObjectKeys: getObjectKeys,
        groupAndMerge: groupAndMerge,
        func: func,
      }}
      components={{
        Recharts,
      }}
      jsx={code}
    />
  )
}

const JsxDisplay = (props: Props) => {
  const { code, data, graph_ref } = props

  let visData = data
  // Current safeguard for rendering performance issues
  if (visData.length > 10000) {
    console.warn("Data too large, only rendering first 10000 rows")
    visData = visData.slice(0, 10000)
  }

  let global_idx = 0
  const getColors = () => {
    // Color schemes taken from https://github.gamma.bcg.com/pages/Shora-Andy/gamma.ui/?path=/docs/intro-color-palettes--bg-scale#qualitative-color-palettes
    const color_scheme = [
      /* "#e3e2dd", */ "#30c0a4",
      "#4c5460",
      "#a5a15f",
      "#6a93c4",
      "#e41c54",
      "#106840",
      "#3dab93",
      "#d3d539",
      "#a1d1e7",
      "#640c34",
      "#555f90",
      "#ece79d",
      "#7b7574",
      "#995c54",
      "#e6bc87",
      "#d49b80",
      "#b8c060",
      "#47785e",
      "#346444",
    ]
    // const color_scheme_alt = ["#00d870","#146145","#5188c8","#c7c7c7","#45cee3","#875484","#ea5353","#bf6363","#1a94a0","#94a0b7","#becc72","#3709d1"]
    // alternative2 = [
    //     "#5dfdb0", "#39b27c", "#156648",
    //     "#76d6e5", "#4a8da1", "#1e445c",
    //     "#ffb74d", "#ff9800", "#8f4700",
    //     "#ff5638", "#e10909", "#760505",
    // ]
    const color = color_scheme[global_idx % color_scheme.length]
    global_idx += 1
    return color
  }

  const groupAndMerge = (data: any[], groupField: string, keyField: string, valueField: string) => {
    const groupedData = groupBy(data, groupField)
    const groupedAndMergedData = Object.keys(groupedData).map((group) =>
      groupedData[group].reduce(
        (result, row) => ({
          ...result,
          [get(row, keyField, "default")]: get(row, valueField, "default"),
        }),
        {}
      )
    )
    return groupedAndMergedData
  }

  const getObjectKeys = (obj) => Object.keys(first(obj) || {})
  const func = (funcBody, ...args) => {
    const F = new Function(...args, funcBody)
    return F
  }

  return (
    <Recharts.ResponsiveContainer width="100%" height={750}>
      <ResponsiveWrapper
        data={visData}
        code={code}
        graph_ref={graph_ref}
        getColors={getColors}
        groupAndMerge={groupAndMerge}
        getObjectKeys={getObjectKeys}
        func={func}
      />
    </Recharts.ResponsiveContainer>
  )
}

export default JsxDisplay
