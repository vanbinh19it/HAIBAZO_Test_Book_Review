import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { ApiError, OpenAPI } from "./client"
import { ThemeProvider } from "./components/theme-provider"
import { Toaster } from "./components/ui/sonner"
import "./index.css"
import { routeTree } from "./routeTree.gen"

OpenAPI.BASE = import.meta.env.VITE_API_URL
OpenAPI.TOKEN = async () => {
  return localStorage.getItem("access_token") || ""
}

// Migrate old dark preference to light so UI updates immediately.
const savedTheme = localStorage.getItem("vite-ui-theme")
if (savedTheme === "dark") {
  localStorage.setItem("vite-ui-theme", "light")
}

const redirectToLogin = () => {
  localStorage.removeItem("access_token")
  window.location.href = "/login"
}

const handleApiError = (error: Error) => {
  if (!(error instanceof ApiError)) {
    return
  }

  const isAuthError = [401, 403].includes(error.status)
  const isStaleUserTokenError =
    error.status === 404 &&
    (error.url.endsWith("/api/v1/users/me") ||
      error.request.url === "/api/v1/users/me")

  if (isAuthError || isStaleUserTokenError) {
    redirectToLogin()
  }
}
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <Toaster richColors closeButton />
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>,
)
