// Reduce bundle size by only importing the plotly modules we need (https://github.com/plotly/react-plotly.js/issues/72#issuecomment-379578461)
//@ts-ignore
import Plotly from "plotly.js-dist-min"
//@ts-ignore
import createPlotlyComponent from "react-plotly.js/factory"

const Plot = createPlotlyComponent(Plotly)

interface Props {
  code: string
}

const PlotlyDisplay = (props: Props) => {
  const { code } = props
  const DATA_JSON = JSON.parse(code)
  const { data, layout } = {
    data: DATA_JSON.data,
    layout: DATA_JSON.layout,
  } || { data: [], layout: {} }
  return (
    <div className="flex h-full w-full flex-col items-center justify-center">
      <Plot
        className="flex h-full w-full flex-col items-center justify-center"
        data={data}
        layout={layout}
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  )
}

export default PlotlyDisplay
