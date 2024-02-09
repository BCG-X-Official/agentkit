import { HTML_FONT_SIZE } from "../Theme.types"

export const DEFAULT_MIN_SCREEN = 360
export const DEFAULT_MAX_SCREEN = 1600

/**
 * It returns a CSS `clamp` function string that will fluidly
 * transition between a `minSize` and `maxSize` based on the screen size provided
 */
export const createFluidValue = (minSize: number, maxSize: number, defaultBaseSize = HTML_FONT_SIZE) => {
  return `clamp(${pxToRem(minSize, defaultBaseSize)}, ${getPreferredValue(
    minSize,
    maxSize,
    DEFAULT_MIN_SCREEN,
    DEFAULT_MAX_SCREEN,
    defaultBaseSize
  )}, ${pxToRem(maxSize, defaultBaseSize)})`
}

/**
 * Determines how fluid typography scales
 */
const getPreferredValue = (
  minSize: number,
  maxSize: number,
  minScreenSize: number,
  maxScreenSize: number,
  defaultBaseSize: number
) => {
  const vwCalc = cleanNumber((100 * (maxSize - minSize)) / (maxScreenSize - minScreenSize))
  const remCalc = cleanNumber((minScreenSize * maxSize - maxScreenSize * minSize) / (minScreenSize - maxScreenSize))

  return `${vwCalc}vw + ${pxToRem(remCalc, defaultBaseSize)}`
}

const pxToRem = (px: number | string, defaultBaseSize: number) => `${cleanNumber(Number(px) / defaultBaseSize)}rem`

const cleanNumber = (num: number) => Math.round((num + Number.EPSILON) * 100) / 100
