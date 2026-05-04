import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type BookCreate, AuthorsService, BooksService } from "@/client"
import CreateBook, {
  type CreateBookFormData,
} from "@/components/Books/CreateBook"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  title: z.string().trim().min(1, { message: "Title is required" }),
  author_id: z
    .number({ message: "Author is required" })
    .int()
    .positive({ message: "Author is required" }),
})

function getAuthorsQueryOptions() {
  return {
    queryFn: () => AuthorsService.readAuthors({ page: 1, pageSize: 100 }),
    queryKey: ["authors", "select-options"],
  }
}

export const Route = createFileRoute("/_layout/books/create")({
  component: CreateBookPage,
  head: () => ({
    meta: [
      {
        title: "Create Book",
      },
    ],
  }),
})

function CreateBookPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { data: authors, isLoading: isLoadingAuthors } = useQuery(
    getAuthorsQueryOptions(),
  )

  const form = useForm<CreateBookFormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: "",
      author_id: 0,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: BookCreate) => BooksService.createBook({ requestBody: data }),
    onSuccess: async () => {
      showSuccessToast("Book created successfully")
      await queryClient.invalidateQueries({ queryKey: ["books"] })
      navigate({ to: "/books" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: CreateBookFormData) => {
    mutation.mutate(data)
  }

  return (
    <div className="flex flex-col gap-6">
      
      <CreateBook
        form={form}
        onSubmit={onSubmit}
        isSubmitting={mutation.isPending || isLoadingAuthors}
        authors={authors?.data ?? []}
      />
    </div>
  )
}
