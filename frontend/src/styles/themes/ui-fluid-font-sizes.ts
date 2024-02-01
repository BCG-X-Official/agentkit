import { type UISIzes } from "~/styles/themes"

import { createFluidValue } from "./utils/create-fluid-value"

export const UI_FLUID_FONT_SIZES: Record<`fluid-${UISIzes}`, [string, Record<string, string | number>]> = {
  "fluid-c3xs": [createFluidValue(2, 4), { lineHeight: "10px" }],
  "fluid-c2xs": [createFluidValue(4, 8), { lineHeight: createFluidValue(8, 12) }],
  "fluid-cxs": [createFluidValue(4, 12), { lineHeight: createFluidValue(12, 20) }],
  "fluid-csm": [createFluidValue(12, 16), { lineHeight: createFluidValue(20, 28) }],
  "fluid-cmd": [createFluidValue(16, 24), { lineHeight: createFluidValue(28, 36) }],
  "fluid-clg": [createFluidValue(24, 32), { lineHeight: createFluidValue(36, 44) }],
  "fluid-cxl": [createFluidValue(32, 48), { lineHeight: createFluidValue(44, 52) }],
  "fluid-c2xl": [createFluidValue(48, 64), { lineHeight: 1.3 }],
  "fluid-c3xl": [createFluidValue(64, 81), { lineHeight: 1.3 }],
}
