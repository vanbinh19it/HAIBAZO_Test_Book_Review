import { BookUser, Briefcase, MessageSquare, Users } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

const baseItems: Item[] = [
  {
    icon: BookUser,
    title: "Authors",
    path: "/authors",
    children: [
      { title: "List", path: "/authors" },
      { title: "Create", path: "/authors/create" },
    ],
  },
  {
    icon: Briefcase,
    title: "Books",
    path: "/books",
    children: [
      { title: "List", path: "/books" },
      { title: "Create", path: "/books/create" },
    ],
  },
  {
    icon: MessageSquare,
    title: "Reviews",
    path: "/reviews",
    children: [
      { title: "List", path: "/reviews" },
      { title: "Create", path: "/reviews/create" },
    ],
  },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()

  const items = currentUser?.is_superuser
    ? [...baseItems, { icon: Users, title: "Admin", path: "/admin" }]
    : baseItems

  return (
    <Sidebar collapsible="icon">
      <SidebarContent className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Main items={items} />
      </SidebarContent>
      <User user={currentUser} />
    </Sidebar>
  )
}

export default AppSidebar
