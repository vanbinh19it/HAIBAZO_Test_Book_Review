import type { ReviewPublic } from "@/client"
import type { ColumnDef } from "@tanstack/react-table"
import { ReviewActionsMenu } from "./ReviewActionsMenu"

export const reviewColumns: ColumnDef<ReviewPublic>[] = [
  {
    id: "no",
    header: "No",
    cell: ({ row }) => row.original.id,
  },
  {
    id: "book",
    header: "Book",
    cell: ({ row }) => row.original.book_title ?? "-",
  },
  {
    id: "author",
    header: "Author",
    cell: ({ row }) => row.original.author_name ?? "-",
  },
  {
    accessorKey: "content",
    header: "Review",
    cell: ({ row }) => <span className="line-clamp-2">{row.original.content}</span>,
  },
  {
    id: "actions",
    header: () => <div className="text-center">Actions</div>,
    size: 100,
    cell: ({ row }) => (
      <div className="flex justify-center">
        <ReviewActionsMenu review={row.original} />
      </div>
    ),
  },
]

