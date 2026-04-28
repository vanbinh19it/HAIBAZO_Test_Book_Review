import { useSuspenseQuery } from "@tanstack/react-query"
import type { OnChangeFn, PaginationState } from "@tanstack/react-table"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useMemo, useState } from "react"

import { AuthorsService, BooksService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingBooks from "@/components/Pending/PendingBooks"
import { getBookColumns } from "@/components/Books/columns"

function getBooksQueryOptions(page: number, pageSize: number) {
  return {
    queryFn: () => BooksService.readBooks({ page, pageSize }),
    queryKey: ["books", page, pageSize],
  }
}

function getAuthorsQueryOptions() {
  return {
    queryFn: () => AuthorsService.readAuthors({ page: 1, pageSize: 100 }),
    queryKey: ["authors", "select-options"],
  }
}

export const Route = createFileRoute("/_layout/books/")({
  component: BooksListPage,
  head: () => ({
    meta: [
      {
        title: "Books List - FastAPI Template",
      },
    ],
  }),
})

function BooksTableContent({
  pagination,
  onPaginationChange,
}: {
  pagination: PaginationState
  onPaginationChange: OnChangeFn<PaginationState>
}) {
  const { data: books } = useSuspenseQuery(
    getBooksQueryOptions(pagination.pageIndex + 1, pagination.pageSize),
  )
  const { data: authors } = useSuspenseQuery(getAuthorsQueryOptions())
  const columns = useMemo(() => getBookColumns(authors.data), [authors.data])

  if (books.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 rounded-full bg-muted p-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any books yet</h3>
        <p className="text-muted-foreground">Create your first book to get started</p>
      </div>
    )
  }

  return (
    <DataTable
      columns={columns}
      data={books.data}
      paginationState={pagination}
      onPaginationChange={onPaginationChange}
      manualPagination
      rowCount={books.count}
      pageCount={books.total_pages ?? 1}
      pageSizeOptions={[5]}
    />
  )
}

function BooksTable({
  pagination,
  onPaginationChange,
}: {
  pagination: PaginationState
  onPaginationChange: OnChangeFn<PaginationState>
}) {
  return (
    <Suspense fallback={<PendingBooks />}>
      <BooksTableContent
        pagination={pagination}
        onPaginationChange={onPaginationChange}
      />
    </Suspense>
  )
}

function BooksListPage() {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 5,
  })

  return (
    <div className="flex flex-col gap-6">
      <BooksTable pagination={pagination} onPaginationChange={setPagination} />
    </div>
  )
}
