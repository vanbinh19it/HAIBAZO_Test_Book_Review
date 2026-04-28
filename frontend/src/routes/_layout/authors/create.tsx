import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type AuthorCreate, AuthorsService } from "@/client"
import CreateAuthor, {
  type CreateAuthorFormData,
} from "@/components/Authors/CreateAuthor"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  name: z.string().trim().min(1, { message: "Name is required" }),
})

export const Route = createFileRoute("/_layout/authors/create")({
  component: CreateAuthorPage,
  head: () => ({
    meta: [
      {
        title: "Create Author",
      },
    ],
  }),
})

function CreateAuthorPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const form = useForm<CreateAuthorFormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: AuthorCreate) =>
      AuthorsService.createAuthor({ requestBody: data }),
    onSuccess: async () => {
      showSuccessToast("Author created successfully")
      await queryClient.invalidateQueries({ queryKey: ["authors"] })
      navigate({ to: "/authors" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: CreateAuthorFormData) => {
    mutation.mutate(data)
  }

  return (
    <div className="flex flex-col gap-6">
     
      <CreateAuthor
        form={form}
        onSubmit={onSubmit}
        isSubmitting={mutation.isPending}
      />
    </div>
  )
}
