import type { Session } from '~/types/clinic'

export function useAuth() {
  const session = useState<Session | null>('session', () => null)
  const request = useRequestFetch()

  async function loadSession() {
    const result = await request<{ user: Session | null }>('/api/session')
    session.value = result.user
    return session.value
  }

  async function signOut() {
    await $fetch('/api/sign-out', { method: 'POST', body: {} })
    session.value = null
    clearNuxtData()
    await navigateTo('/login')
  }

  return { session, loadSession, signOut }
}
