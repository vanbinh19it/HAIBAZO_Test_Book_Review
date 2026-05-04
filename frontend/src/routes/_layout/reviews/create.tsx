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

// Explanation:
// The issue is related to validation mode in react-hook-form. With 'onBlur' mode, validation messages will only appear for each field *after* it has been blurred (touched and left). 
// This means if you immediately submit the form with both fields empty, only *one* field's error shows up, usually the first one, not both at once.
// To show all validation error messages for all fields simultaneously when the user submits (even untouched fields), you should switch the form mode to "onTouched" or "onSubmit", and set `shouldFocusError: false` to avoid auto-focusing and only show all messages.

const formSchema = z.object({
  book_id: z
    .number()
    .refine((value) => Number.isInteger(value) && value > 0, {
      message: "Please select book",
    }),
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
    // Change mode to "onSubmit" to show all errors on submit
    mode: "onSubmit",
    criteriaMode: "all",
    defaultValues: {
      book_id: 0,
      content: "",
    },
    shouldFocusError: false, // Don't auto focus the first error, allow user to see all at once
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
