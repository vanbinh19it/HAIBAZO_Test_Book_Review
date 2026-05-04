import type { UseFormReturn } from "react-hook-form"

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"

export type CreateAuthorFormData = {
  name: string
}

interface CreateAuthorProps {
  form: UseFormReturn<CreateAuthorFormData>
  onSubmit: (data: CreateAuthorFormData) => void
  isSubmitting: boolean
}

export default function CreateAuthor({
  form,
  onSubmit,
  isSubmitting,
}: CreateAuthorProps) {
  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="w-full space-y-6 md:w-1/2"
      >
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Name <span className="text-destructive">*</span>
              </FormLabel>
              <FormControl>
                <Input
                  id="author-name"
                  className="h-10"
                  placeholder="Author name"
                  type="text"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end">
          <LoadingButton type="submit" loading={isSubmitting} className="min-w-24">
            Create
          </LoadingButton>
        </div>
      </form>
    </Form>
  )
}
