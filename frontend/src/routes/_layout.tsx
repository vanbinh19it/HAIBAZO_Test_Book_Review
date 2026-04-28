import { createFileRoute, Outlet, redirect, useRouterState } from "@tanstack/react-router"

import DashboardPageHeader from "@/components/Common/DashboardPageHeader"
import { Footer } from "@/components/Common/Footer"
// import { Logo } from "@/components/Common/Logo"
import { TopHeader } from "@/components/Common/TopHeader"
import AppSidebar from "@/components/Sidebar/AppSidebar"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { getInitials } from "@/utils"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  const { user } = useAuth()
  const pathname = useRouterState({ select: (state) => state.location.pathname })
  const pageTitle = getDashboardHeaderTitle(pathname)

  return (
    <SidebarProvider className="min-h-svh bg-background pt-16">
      <TopHeader />
      <AppSidebar />

      <SidebarInset className="bg-background">
        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center justify-between gap-4 border-b border-border bg-background px-4 md:px-8">
          <div className="flex min-w-0 items-center gap-2">
            <SidebarTrigger className="-ml-1 text-muted-foreground" />
            <DashboardPageHeader
              title={pageTitle}
              className="min-w-0"
              titleClassName="truncate text-sm text-muted-foreground"
            />
          </div>
          <div className="flex items-center gap-2 text-sm text-foreground">
            <Avatar className="size-8">
              <AvatarFallback className="bg-zinc-600 text-white">
                {getInitials(user?.full_name || "User")}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col items-start min-w-0">
              <p className="text-sm font-medium truncate w-full">{user?.full_name ?? "User"}</p>
              <p className="text-xs text-muted-foreground truncate w-full">{user?.email}</p>
            </div>
       
          </div>
     
        </header>
        <main className="flex-1 p-8">
          <div className="mx-auto flex w-full max-w-7xl flex-col gap-8">
            <Outlet />
          </div>
        </main>
        <Footer />
      </SidebarInset>
    </SidebarProvider>
  )
}

function getDashboardHeaderTitle(pathname: string) {
  const segments = pathname.split("/").filter(Boolean)
  if (segments.length === 0) {
    return "Dashboard"
  }

  const [section, page] = segments
  const sectionTitle = capitalize(section)

  if (!page) {
    return `${sectionTitle} > List`
  }

  return `${sectionTitle} > ${capitalize(page)}`
}

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export default Layout
