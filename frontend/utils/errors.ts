export function errorMessage(error: unknown): string {
  const value = error as {
    data?: { message?: string; statusMessage?: string }
    message?: string
  }
  return (
    value?.data?.message ||
    value?.data?.statusMessage ||
    'Unable to connect. Please try again.'
  )
}
