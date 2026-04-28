import { Link as RouterLink, useRouterState } from "@tanstack/react-router"
import { ChevronRight, type LucideIcon } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  useSidebar,
} from "@/components/ui/sidebar"

export type Item = {
  icon: LucideIcon
  title: string
  path: string
  children?: Array<{
    title: string
    path: string
  }>
}

interface MainProps {
  items: Item[]
}

const sidebarMenuButtonClassName =
  "rounded-lg px-3 py-2.5 text-[13px] font-medium text-sidebar-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:text-sidebar-accent-foreground hover:bg-sidebar-accent [&>svg]:stroke-[1.5]"

const sidebarMenuSubButtonClassName =
  "rounded-lg text-[12px] text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:text-sidebar-accent-foreground"

export function Main({ items }: MainProps) {
  const { isMobile, setOpenMobile } = useSidebar()
  const router = useRouterState()
  const currentPath = router.location.pathname
  const [openMenus, setOpenMenus] = useState<Record<string, boolean>>({})

  const activeMenuTitles = useMemo(
    () =>
      items
        .filter(
          (item) =>
            item.children?.some((child) => child.path === currentPath) ?? false,
        )
        .map((item) => item.title),
    [items, currentPath],
  )

  useEffect(() => {
    if (activeMenuTitles.length === 0) return

    setOpenMenus((prev) => {
      const next = { ...prev }
      activeMenuTitles.forEach((title) => {
        next[title] = true
      })
      return next
    })
  }, [activeMenuTitles])

  const handleMenuClick = () => {
    if (isMobile) {
      setOpenMobile(false)
    }
  }

  const toggleMenu = (title: string) => {
    setOpenMenus((prev) => ({
      ...prev,
      [title]: !prev[title],
    }))
  }

  return (
    <SidebarGroup>
      <SidebarGroupContent>
        <SidebarMenu>
          {items.map((item) => {
            const isActive =
              currentPath === item.path ||
              item.children?.some((child) => child.path === currentPath) ||
              false

            return (
              <SidebarMenuItem key={item.title}>
                {item.children && item.children.length > 0 ? (
                  <SidebarMenuButton
                    tooltip={item.title}
                    isActive={isActive}
                    className={sidebarMenuButtonClassName}
                    onClick={() => toggleMenu(item.title)}
                  >
                    <item.icon />
                    <span>{item.title}</span>
                    <ChevronRight
                      className={`ml-auto transition-transform ${
                        openMenus[item.title] ? "rotate-90" : ""
                      }`}
                    />
                  </SidebarMenuButton>
                ) : (
                  <SidebarMenuButton
                    tooltip={item.title}
                    isActive={isActive}
                    className={sidebarMenuButtonClassName}
                    asChild
                  >
                    <RouterLink to={item.path} onClick={handleMenuClick}>
                      <item.icon />
                      <span>{item.title}</span>
                    </RouterLink>
                  </SidebarMenuButton>
                )}
                {item.children && item.children.length > 0 && openMenus[item.title] ? (
                  <SidebarMenuSub>
                    {item.children.map((child) => (
                      <SidebarMenuSubItem key={`${item.title}-${child.title}`}>
                        <SidebarMenuSubButton
                          asChild
                          isActive={currentPath === child.path}
                          className={sidebarMenuSubButtonClassName}
                        >
                          <RouterLink to={child.path} onClick={handleMenuClick}>
                            <span>{child.title}</span>
                          </RouterLink>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    ))}
                  </SidebarMenuSub>
                ) : null}
              </SidebarMenuItem>
            )
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}
