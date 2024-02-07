import Icon from "@/components/CustomIcons/Icon"

const actions = {
  sql_tool: {
    icon: () => <Icon.BiCodeAlt className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Searching proprietary database...",
  },
  list_tables_sql_db: {
    icon: () => <Icon.BsDatabase className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Listing tables in database...",
  },
  schema_sql_db: {
    icon: () => <Icon.BiTable className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Getting schema of database...",
  },
  validate_sql_query: {
    icon: (metadata: { [key: string]: string }) =>
      metadata.success ? (
        <Icon.BiCheck className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />
      ) : (
        <Icon.BiX className="mb-1 mr-2 h-auto w-6 text-rose-600" />
      ),
    text: () => "Validating query...",
  },
  improve_sql_query: {
    icon: () => <Icon.BiPencil className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Improving query...",
  },
  visualizer_tool: {
    icon: () => <Icon.BiBarChart className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Using visualizer tool...",
  },
  build_visualization: {
    icon: () => <Icon.BiBarChart className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Building visualization...",
  },
  summarizer_tool: {
    icon: () => <Icon.BiText className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Summarizing...",
  },
  expert_tool: {
    icon: () => <Icon.BiUser className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Using expert tool...",
  },
  entertainer_tool: {
    icon: () => <Icon.BiUser className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Writing initial response while researching...",
  },
  error: {
    icon: () => <Icon.BiX className="mb-1 mr-2 h-auto w-6 text-rose-600" />,
    text: () => "Error while running, please report to the administrator",
  },
  no_data: {
    icon: () => <Icon.BiX className="mb-1 mr-2 h-auto w-6 text-rose-600" />,
    text: () => "No data found",
  },
  pdf_tool: {
    icon: () => <Icon.BiFile className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Searching in PDF documents...",
  },
  filter_docs: {
    icon: () => <Icon.BiListCheck className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Filter for relevant documents...",
  },
  qa_pdf_docs: {
    icon: () => <Icon.BiBook className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Answering questions about PDF documents...",
  },
  image_generation_tool: {
    icon: () => <Icon.BiPaint className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Generating the image...",
  },
  clarify_tool: {
    icon: () => <Icon.BiCommentAdd className="text-bcg-green-light mb-1 mr-2 h-auto w-6" />,
    text: () => "Clarifying the user request...",
  },
}

export default actions
