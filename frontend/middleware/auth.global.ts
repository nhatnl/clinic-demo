export default defineNuxtRouteMiddleware(async (to) => {
  const { loadSession } = useAuth()
  const session = await loadSession()
  if (!session && to.path !== '/login') return navigateTo('/login')
  if (session && to.path === '/login') return navigateTo('/consultations')
  if (to.path.startsWith('/admin') && session?.role !== 1)
    return navigateTo('/consultations')
})
