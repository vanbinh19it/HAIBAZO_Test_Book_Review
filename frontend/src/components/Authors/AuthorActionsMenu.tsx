import type { AuthorPublic } from "@/client"
import DeleteAuthor from "./DeleteAuthor"
import EditAuthor from "./EditAuthor"

interface AuthorActionsMenuProps {
  author: AuthorPublic
}

export const AuthorActionsMenu = ({ author }: AuthorActionsMenuProps) => {
  return (
    <div className="inline-flex items-center gap-1">
      <EditAuthor author={author} />
      <DeleteAuthor id={author.id} />
    </div>
  )
}
