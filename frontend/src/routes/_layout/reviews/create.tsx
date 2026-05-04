import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type ReviewCreate, BooksService, ReviewsService } from "@/client"
import CreateReview, {
  type CreateReviewFormData,
} from "@/components/Reviews/CreateReview"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  book_id: z.number({ message: "Please select  book" }).int().positive(),
  content: z.string().trim().min(1, { message: "Please enter review" }),
})

function getBooksQueryOptions() {
  return {
    queryFn: () => BooksService.readBooks({ page: 1, pageSize: 100 }),
    queryKey: ["books", "select-options"],
  }
}

export const Route = createFileRoute("/_layout/reviews/create")({
  component: CreateReviewPage,
  head: () => ({
    meta: [
      {
        title: "Create Review",
      },
    ],
  }),
})

function CreateReviewPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { data: books, isLoading: isLoadingBooks } = useQuery(getBooksQueryOptions())

  const form = useForm<CreateReviewFormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      book_id: 0,
      content: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ReviewCreate) => ReviewsService.createReview({ requestBody: data }),
    onSuccess: async () => {
      showSuccessToast("Review created successfully")
      await queryClient.invalidateQueries({ queryKey: ["reviews"] })
      navigate({ to: "/reviews" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: CreateReviewFormData) => {
    mutation.mutate(data)
  }

  return (
    <div className="flex flex-col gap-6">
      
      <CreateReview
        form={form}
        onSubmit={onSubmit}
        isSubmitting={mutation.isPending || isLoadingBooks}
        books={books?.data ?? []}
      />
    </div>
  )
}

