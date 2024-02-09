import { type UISIzes } from "~/styles/themes"

export const UI_FONT_SIZES: Record<UISIzes, [string, Record<string, string | number>]> = {
  c3xs: ["2px", { lineHeight: "8px" }],
  c2xs: ["4px", { lineHeight: "8px" }],
  cxs: ["8px", { lineHeight: "12px" }],
  csm: ["12px", { lineHeight: "16px" }],
  cmd: ["16px", { lineHeight: "24px" }],
  clg: ["24px", { lineHeight: "32px" }],
  cxl: ["32px", { lineHeight: "36px" }],
  c2xl: ["48px", { lineHeight: 1 }],
  c3xl: ["64px", { lineHeight: 1 }],
}
