export const formatDate = (dateString: string) => {
  if (!dateString) {
    return ""
  }

  const date = new Date(dateString)
  return new Intl.DateTimeFormat("en-US").format(date)
}
