import { SidebarTrigger } from "@/components/ui/sidebar"

export function TopHeader() {
  return (
    <header className="fixed inset-x-0 top-0 z-30 flex h-16 items-center gap-3 border-b border-zinc-700 bg-zinc-800 px-4 text-white md:px-8">
    <SidebarTrigger className="-ml-1 text-zinc-200 hover:bg-zinc-700 hover:text-white" />
      <h1 className="text-base font-semibold tracking-wide uppercase">
        HAIBAZO BOOK REVIEW
      </h1>
    </header>
  )
}

export default TopHeader
