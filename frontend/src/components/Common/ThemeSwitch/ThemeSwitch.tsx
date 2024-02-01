import { useTheme } from "next-themes"
import Icon from "~/components/CustomIcons/Icon"

export const ThemeSwitch = () => {
  const { theme, setTheme } = useTheme()

  return (
    <label className="daisyswap daisyswap-rotate">
      <input
        type="checkbox"
        className="daisytheme-controller cursor-pointer"
        value={theme}
        onChange={() => (theme === "dark" ? setTheme("light") : setTheme("dark"))}
      />
      {theme === "light" ? (
        <Icon.MdOutlineWbSunny className="!text-fluid-cmd hover:!scale-110 hover:!opacity-60" />
      ) : (
        <Icon.FiMoon className="!text-fluid-cmd hover:!scale-110 hover:!opacity-60" />
      )}
    </label>
  )
}
