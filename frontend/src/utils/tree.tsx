import Icon from "~/components/CustomIcons/Icon"
import ThreeDotsLoader from "~/components/CustomIcons/ThreeDotsLoader"

export interface TreeItem {
  id: string
  title: string
  icon?: React.ReactElement
  status?: React.ReactElement | string
  children?: TreeItem[]
}

export interface TreeItemData<T> extends Omit<TreeItem, "children"> {
  children?: TreeItemData<T>[]
  data: T
}

export interface ListItem {
  id: string
  number?: string
  title?: string
  dmetadata?: Record<string, any>
  icon?: string
  data?: string
}

export interface ActionItem {
  id: string
  parent_id?: string
  data?: string
  icon?: string
  dmetadata?: Record<string, any>
  loading?: boolean
}

export function buildSectionTree(list: ListItem[], expanded: boolean = false): TreeItemData<ListItem>[] {
  /*
    Function to build a tree based on the section numbers (e.g. 1.1, 1.1.2, 1.1.3, 1.2, 2, etc.).
    Assumes numbers to be unique per section, otherwise overwrites.
  */
  const roots: Record<string, TreeItemData<ListItem>> = {}
  const allNodes: Record<string, TreeItemData<ListItem>> = {}

  // Iterate over the list to create nodes and build parent-child relationships
  list.forEach((item) => {
    const newNode = {
      id: item.id!,
      title: expanded ? `${item.number} ${item.title}` : item.number!,
      status: item.dmetadata?.["page"] ? `${item.dmetadata?.["page"]}` : undefined,
      data: item,
    }
    // Create/Overwrite node
    allNodes[item.number!] = newNode

    // For root node, add it directly to roots
    if (!item.number!.includes(".")) {
      roots[item.number!] = newNode
      return
    }

    // If not a root node, find the closest existing parent and add the node to parent's children
    // Start with direct parent and if not found, go one level higher, until a parent or root is found
    let parentNumber = item.number!
    let parentNode

    do {
      parentNumber = parentNumber.substring(0, parentNumber.lastIndexOf("."))
      parentNode = allNodes[parentNumber]
    } while (!parentNode && parentNumber.includes("."))

    if (parentNode) {
      if (!parentNode.children) parentNode.children = []
      parentNode.children.push(newNode)
    } else {
      // If no parent was found through the loop it should be a root
      roots[parentNumber] = newNode
    }
  })

  return Object.values(roots)
}

const supportedIcons = {
  TbWriting: Icon.TbWriting,
  AiOutlineFileSearch: Icon.AiOutlineFileSearch,
  TfiWrite: Icon.TfiWrite,
  TbSection: Icon.TbSection,
  BiErrorAlt: Icon.BiErrorAlt,
  SiWritedotas: Icon.SiWritedotas,
  MdOutlineQuickreply: Icon.MdOutlineQuickreply,
  RiDraftLine: Icon.RiDraftLine,
  BiCheck: Icon.BiCheck,
  AiOutlineStop: Icon.AiOutlineStop,
  GrDocumentStore: Icon.GrDocumentStore,
}

export function buildActionTree(list: ActionItem[]): TreeItemData<ActionItem>[] {
  const roots: Record<string, TreeItemData<ActionItem>> = {}
  const allNodes: Record<string, TreeItemData<ActionItem>> = {}

  list.forEach((item) => {
    const icon = item.icon || "BiQuestionMark"
    const IconComponent = supportedIcons[icon as keyof typeof supportedIcons] || Icon.BiErrorAlt

    let status = <Icon.BiCheck />
    if (item.loading) {
      status = <ThreeDotsLoader />
    } else if (item.dmetadata?.result) {
      status = item.dmetadata?.result
    } else if (item.dmetadata?.cancelled) {
      status = <Icon.AiOutlineStop />
    }

    const newNode = {
      id: item.id!,
      title: item.data || "Unknown action",
      icon: <IconComponent />,
      status: status,
      data: item,
    } as TreeItemData<ActionItem>

    allNodes[item.id!] = newNode
  })

  Object.values(allNodes).forEach((item) => {
    if (!item.data.parent_id) {
      roots[item.id!] = item
    } else {
      const parent = allNodes[item.data.parent_id]
      if (parent) {
        if (!parent.children) parent.children = []
        parent.children.push(item)
      }
    }
  })

  return Object.values(roots)
}
