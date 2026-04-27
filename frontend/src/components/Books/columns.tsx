import type { AuthorPublic, BookPublic } from "@/client"
import type { ColumnDef } from "@tanstack/react-table"
import { BookActionsMenu } from "./BookActionsMenu"

export const getBookColumns = (
  authors: AuthorPublic[],
): ColumnDef<BookPublic>[] => [
  {
    id: "no",
    header: "No",
    cell: ({ row }) => row.original.id,
  },
  {
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => <span className="font-medium">{row.original.title}</span>,
  },
  {
    id: "author",
    header: "Author",
    cell: ({ row }) => row.original.author_name ?? "-",
  },
  {
    id: "actions",
    header: () => <div className="text-center">Actions</div>,
    size: 100,
    cell: ({ row }) => (
      <div className="flex justify-center">
        <BookActionsMenu book={row.original} authors={authors} />
      </div>
    ),
  },
]
