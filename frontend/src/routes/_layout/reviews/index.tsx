import { useSuspenseQuery } from "@tanstack/react-query"
import type { OnChangeFn, PaginationState } from "@tanstack/react-table"
import { createFileRoute } from "@tanstack/react-router"
import { Search } from "lucide-react"
import { Suspense, useState } from "react"

import { ReviewsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingReviews from "@/components/Pending/PendingReviews"
import { reviewColumns } from "@/components/Reviews/columns"

function getReviewsQueryOptions(page: number, pageSize: number) {
  return {
    queryFn: () => ReviewsService.readReviews({ page, pageSize }),
    queryKey: ["reviews", page, pageSize],
  }
}

export const Route = createFileRoute("/_layout/reviews/")({
  component: ReviewsListPage,
  head: () => ({
    meta: [
      {
        title: "Reviews List - FastAPI Template",
      },
    ],
  }),
})

function ReviewsTableContent({
  pagination,
  onPaginationChange,
}: {
  pagination: PaginationState
  onPaginationChange: OnChangeFn<PaginationState>
}) {
  const { data: reviews } = useSuspenseQuery(
    getReviewsQueryOptions(pagination.pageIndex + 1, pagination.pageSize),
  )

  if (reviews.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 rounded-full bg-muted p-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">You don't have any reviews yet</h3>
        <p className="text-muted-foreground">Create your first review to get started</p>
      </div>
    )
  }

  return (
    <DataTable
      columns={reviewColumns}
      data={reviews.data}
      paginationState={pagination}
      onPaginationChange={onPaginationChange}
      manualPagination
      rowCount={reviews.count}
      pageCount={reviews.total_pages ?? 1}
      pageSizeOptions={[5]}
    />
  )
}

function ReviewsTable({
  pagination,
  onPaginationChange,
}: {
  pagination: PaginationState
  onPaginationChange: OnChangeFn<PaginationState>
}) {
  return (
    <Suspense fallback={<PendingReviews />}>
      <ReviewsTableContent
        pagination={pagination}
        onPaginationChange={onPaginationChange}
      />
    </Suspense>
  )
}

function ReviewsListPage() {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 5,
  })

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">Reviews &gt; List</p>
        
      </div>
      <ReviewsTable pagination={pagination} onPaginationChange={setPagination} />
    </div>
  )
}

