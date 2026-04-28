import { SidebarTrigger } from "@/components/ui/sidebar"

export function TopHeader() {
  return (
    <header className="fixed inset-x-0 top-0 z-30 flex h-16 items-center gap-3 border-b border-black/20 bg-header px-4 text-header-foreground md:px-8">
      <SidebarTrigger className="-ml-1 text-header-foreground hover:bg-white/10 hover:text-header-foreground [&_svg]:stroke-[1.5]" />
      <h1 className="text-sm font-semibold tracking-[0.14em] uppercase">
        HAIBAZO BOOK REVIEW
      </h1>
    </header>
  )
}

export default TopHeader
