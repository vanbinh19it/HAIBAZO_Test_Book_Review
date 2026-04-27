import type { ColumnDef } from "@tanstack/react-table"
import type { AuthorPublic } from "@/client"
import { AuthorActionsMenu } from "./AuthorActionsMenu"

export const columns: ColumnDef<AuthorPublic>[] = [
  {
    id: "no",
    header: "No",
    cell: ({ row }) => row.original.id,
  },
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.name}</span>
    ),
  },
  {
    id: "books",
    header: "Books",
    cell: ({ row }) => row.original.books_count ?? 0,
  },
  {
    id: "actions",
    header: () => <div className="text-center">Actions</div>,
    size: 100,
    cell: ({ row }) => (
      <div className="flex justify-center">
        <AuthorActionsMenu author={row.original} />
      </div>
    ),
  },
]
