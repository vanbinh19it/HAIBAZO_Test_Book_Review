import type { ReviewPublic } from "@/client"
import DeleteReview from "./DeleteReview"
import EditReview from "./EditReview"

interface ReviewActionsMenuProps {
  review: ReviewPublic
}

export const ReviewActionsMenu = ({ review }: ReviewActionsMenuProps) => {
  return (
    <div className="inline-flex items-center gap-1">
      <EditReview review={review} />
      <DeleteReview id={review.id} />
    </div>
  )
}

