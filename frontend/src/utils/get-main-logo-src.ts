import { Theme } from "~/styles/themes"

import { LOGO_FULL_DARK_SRC, LOGO_FULL_SRC } from "./constants"

export const getMainLogoSrc = (theme?: string) => {
  if (theme === Theme.Dark) {
    return LOGO_FULL_DARK_SRC
  }

  return LOGO_FULL_SRC
}
