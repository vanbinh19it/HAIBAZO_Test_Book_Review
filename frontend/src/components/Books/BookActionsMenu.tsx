import type { AuthorPublic, BookPublic } from "@/client"
import DeleteBook from "./DeleteBook"
import EditBook from "./EditBook"

interface BookActionsMenuProps {
  book: BookPublic
  authors: AuthorPublic[]
}

export const BookActionsMenu = ({ book, authors }: BookActionsMenuProps) => {
  return (
    <div className="inline-flex items-center gap-1">
      <EditBook book={book} authors={authors} />
      <DeleteBook id={book.id} />
    </div>
  )
}
