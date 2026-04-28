import { useSuspenseQuery } from "@tanstack/react-query"
import type { OnChangeFn, PaginationState } from "@tanstack/react-table"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useState } from "react"

import { AuthorsService } from "@/client"
import { columns } from "@/components/Authors/columns"
import DashboardPageHeader from "@/components/Common/DashboardPageHeader"
import { DataTable } from "@/components/Common/DataTable"
import PendingAuthors from "@/components/Pending/PendingAuthors"

function getAuthorsQueryOptions(page: number, pageSize: number) {
  return {
    queryFn: () => AuthorsService.readAuthors({ page, pageSize }),
    queryKey: ["authors", page, pageSize],
  }
}

export const Route = createFileRoute("/_layout/authors/")({
  component: AuthorsListPage,
  head: () => ({
    meta: [
      {
        title: "Authors List - FastAPI Template",
      },
    ],
  }),
})

function AuthorsTableContent({
  pagination,
  onPaginationChange,
}: {
  pagination: PaginationState
  onPaginationChange: OnChangeFn<PaginationState>
}) {
  const { data: authors } = useSuspenseQuery(
    getAuthorsQueryOptions(pagination.pageIndex + 1, pagination.pageSize),
  )

  if (authors.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 rounded-full bg-muted p-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any authors yet</h3>
        <p className="text-muted-foreground">Create your first author to get started</p>
      </div>
    )
  }

  return (
    <DataTable
      columns={columns}
      data={authors.data}
      paginationState={pagination}
      onPaginationChange={onPaginationChange}
      manualPagination
      rowCount={authors.count}
      pageCount={authors.total_pages ?? 1}
      pageSizeOptions={[5]}
    />
  )
}

function AuthorsTable({
  pagination,
  onPaginationChange,
}: {
  pagination: PaginationState
  onPaginationChange: OnChangeFn<PaginationState>
}) {
  return (
    <Suspense fallback={<PendingAuthors />}>
      <AuthorsTableContent
        pagination={pagination}
        onPaginationChange={onPaginationChange}
      />
    </Suspense>
  )
}

function AuthorsListPage() {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 5,
  })

  return (
    <div className="flex flex-col gap-5">
      <DashboardPageHeader title="Authors > List" />
      <AuthorsTable pagination={pagination} onPaginationChange={setPagination} />
    </div>
  )
}
