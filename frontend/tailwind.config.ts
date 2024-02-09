import { type Config } from "tailwindcss"

import {
  LIGHT_THEME,
  DARK_THEME,
  UI_LAYOUT_SPACINGS,
  UI_FONT_SIZES,
  NEG_UI_LAYOUT_SPACINGS,
  UI_FLUID_FONT_SIZES,
} from "./src/styles/themes"

const defaultTheme = require("tailwindcss/defaultTheme")

export default {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      zIndex: {
        1: "1",
        100: "100",
      },
      fontFamily: {
        sans: ["BCG Sans", ...defaultTheme.fontFamily.sans],
        mono: [...defaultTheme.fontFamily.mono],
        serif: ["BCG Serif", ...defaultTheme.fontFamily.serif],
      },
      spacing: { ...UI_LAYOUT_SPACINGS, ...NEG_UI_LAYOUT_SPACINGS },
      fontSize: { ...UI_FONT_SIZES, ...UI_FLUID_FONT_SIZES },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          ...LIGHT_THEME.colors,
          ...LIGHT_THEME.extendedClasses,
        },
      },
      {
        dark: {
          ...DARK_THEME.colors,
          ...LIGHT_THEME.extendedClasses,
        },
      },
    ],
    prefix: "daisy",
    base: false,
    themeRoot: "*",
  },
} satisfies Config
