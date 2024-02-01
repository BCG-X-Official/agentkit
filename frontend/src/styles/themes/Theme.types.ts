export enum Theme {
  Light = "light",
  Dark = "dark",
  System = "system",
}

export enum BaseUIColor {
  Primary = "primary",
  Secondary = "secondary",
  Accent = "accent",
  Neutral = "neutral",
  Base100 = "base-100",
  Base200 = "base-200",
  Base300 = "base-300",
  Info = "info",
  Success = "success",
  Warning = "warning",
  Error = "error",
}

export enum ExtendedUIClasses {
  InfoVibrantCyan = ".info-vibrant-cyan",
  InfoYellowGreen = ".info-yellow-green",
}

export enum UISIzes {
  C3XS = "c3xs",
  C2XS = "c2xs",
  CXS = "cxs",
  CSM = "csm",
  CMD = "cmd",
  CLG = "clg",
  CXL = "cxl",
  C2XL = "c2xl",
  C3XL = "c3xl",
}

export enum NegUISIzes {
  D3XS = "n3xs",
  N2XS = "n2xs",
  NXS = "nxs",
  NSM = "nsm",
  NMD = "nmd",
  NLG = "nlg",
  NXL = "nxl",
  N2XL = "n2xl",
  N3XL = "n3xl",
}

enum ThemeSection {
  Colors = "colors",
  ExtendedClasses = "extendedClasses",
}

interface ExtendedClassType {
  "background-color"?: string
  color?: string
}

export type UIColorTheme = Partial<
  Record<
    ThemeSection.Colors,
    {
      [key in BaseUIColor]: string
    }
  > &
    Partial<
      Record<
        ThemeSection.ExtendedClasses,
        {
          [key in ExtendedUIClasses]: ExtendedClassType
        }
      >
    >
>

export const HTML_FONT_SIZE = 16
export const HTML_LINE_HEIGHT = 1.5
