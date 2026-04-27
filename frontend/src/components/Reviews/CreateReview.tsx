import type { BookPublic } from "@/client"
import type { UseFormReturn } from "react-hook-form"

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export type CreateReviewFormData = {
  book_id: number
  content: string
}

interface CreateReviewProps {
  form: UseFormReturn<CreateReviewFormData>
  onSubmit: (data: CreateReviewFormData) => void
  isSubmitting: boolean
  books: BookPublic[]
}

export default function CreateReview({
  form,
  onSubmit,
  isSubmitting,
  books,
}: CreateReviewProps) {
  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="w-full space-y-6 md:w-1/2"
      >
        <FormField
          control={form.control}
          name="book_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Book <span className="text-destructive">*</span>
              </FormLabel>
              <FormControl>
                <Select
                  value={field.value ? String(field.value) : undefined}
                  onValueChange={(value) => field.onChange(Number(value))}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select a book" />
                  </SelectTrigger>
                  <SelectContent>
                    {books.map((book) => (
                      <SelectItem key={book.id} value={String(book.id)}>
                        {book.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="content"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Review <span className="text-destructive">*</span>
              </FormLabel>
              <FormControl>
                <textarea
                  className="border-input focus-visible:border-ring focus-visible:ring-ring/50 flex min-h-28 w-full rounded-md border bg-transparent px-3 py-2 text-sm shadow-xs outline-none focus-visible:ring-[3px]"
                  placeholder="Write your review..."
                  {...field}
                  required
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

