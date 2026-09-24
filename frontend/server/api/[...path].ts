import { Buffer } from 'node:buffer'

const cookieName = 'clinic_session'
const endpoints: Record<string, string> = {
  'GET diagnosis': '/diagnosis/',
  'GET consultation': '/consultation',
  'POST consultation': '/consultation',
  'GET patients': '/patients/',
  'POST patients': '/patients/',
  'POST admin/create-user': '/admin/create-user',
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function validDiagnosis(value: unknown): boolean {
  return (
    isRecord(value) &&
    typeof value.code === 'string' &&
    typeof value.name === 'string'
  )
}

function validConsultation(value: unknown): boolean {
  return (
    isRecord(value) &&
    typeof value.id === 'number' &&
    isRecord(value.patient) &&
    typeof value.patient.id === 'number' &&
    typeof value.patient.name === 'string' &&
    typeof value.patient.age === 'number' &&
    typeof value.note === 'string' &&
    typeof value.created_at === 'string' &&
    typeof value.updated_at === 'string' &&
    Array.isArray(value.diagnoses) &&
    value.diagnoses.every(validDiagnosis)
  )
}

function validPatient(value: unknown): boolean {
  return (
    isRecord(value) &&
    typeof value.id === 'number' &&
    typeof value.first_name === 'string' &&
    typeof value.last_name === 'string' &&
    typeof value.age === 'number' &&
    typeof value.gender === 'string'
  )
}

export default defineEventHandler(async (event) => {
  setHeader(event, 'Cache-Control', 'no-store')
  const path = getRouterParam(event, 'path') || ''
  const method = event.method
  // Same-origin mutations plus SameSite cookies protect the cookie-to-bearer bridge.
  if (method !== 'GET') {
    const origin = getHeader(event, 'origin')
    if (origin && origin !== getRequestURL(event).origin) {
      throw createError({ statusCode: 403, message: 'Invalid request origin.' })
    }
    if (!getHeader(event, 'content-type')?.startsWith('application/json')) {
      throw createError({ statusCode: 415, message: 'Requests must use JSON.' })
    }
  }
  if (path === 'sign-out' && method === 'POST') {
    deleteCookie(event, cookieName, { path: '/' })
    return { success: true }
  }

  const token = getCookie(event, cookieName)
  let session: { id: string; role: number; exp: number } | null = null
  if (token) {
    try {
      const claims = JSON.parse(
        Buffer.from(token.split('.')[1] || '', 'base64url').toString(),
      )
      if (
        typeof claims.sub === 'string' &&
        typeof claims.role === 'number' &&
        claims.exp > Date.now() / 1000
      ) {
        session = { id: claims.sub, role: claims.role, exp: claims.exp }
      }
    } catch {
      /* Invalid cookies are removed below. Backend verifies JWT signatures. */
    }
    if (!session) deleteCookie(event, cookieName, { path: '/' })
  }
  // Claims only control UI visibility. FastAPI must verify and authorize data requests.
  if (path === 'session' && method === 'GET')
    return { user: session ? { id: session.id, role: session.role } : null }
  const signingIn = path === 'sign-in' && method === 'POST'
  const patientDetail = method === 'GET' && /^patients\/[1-9]\d*$/.test(path)
  const consultationDetail = method === 'GET' && /^consultation\/[1-9]\d*$/.test(path)
  const endpoint = signingIn
    ? '/auth/sign-in'
    : patientDetail || consultationDetail
      ? `/${path}`
      : endpoints[`${method} ${path}`]
  if (!endpoint)
    throw createError({
      statusCode: 404,
      message: 'This endpoint does not exist.',
    })
  if (!signingIn && !session)
    throw createError({
      statusCode: 401,
      message: 'Your session has expired. Please sign in again.',
    })

  const body = method === 'POST' ? await readBody(event) : undefined
  let result: unknown
  try {
    result = await $fetch(endpoint, {
      baseURL: useRuntimeConfig(event).apiBase,
      method: method as 'GET' | 'POST',
      query: getQuery(event),
      body,
      headers: !signingIn ? { Authorization: `Bearer ${token}` } : undefined,
      retry: 0,
      timeout: 15000,
    })
  } catch (error) {
    const upstream = error as {
      statusCode?: number
      data?: { detail?: string | { msg: string; loc?: string[] }[] }
    }
    const statusCode = upstream.statusCode || 502
    if (statusCode === 401 && !signingIn)
      deleteCookie(event, cookieName, { path: '/' })
    const detail = upstream.data?.detail
    let message = 'The service is unavailable. Please try again later.'
    if (statusCode === 401)
      message = signingIn
        ? 'Incorrect email or password.'
        : 'Your session has expired. Please sign in again.'
    else if (statusCode === 403)
      message = 'You do not have permission to perform this action.'
    else if (statusCode === 404 && path === 'consultation' && method === 'POST' && typeof detail === 'string')
      message = detail
    else if (statusCode === 404 && (patientDetail || consultationDetail))
      message = typeof detail === 'string' ? detail : 'Record not found.'
    else if (statusCode === 404 || statusCode === 405)
      message = 'This feature is not yet available from the backend.'
    else if (statusCode < 500 && Array.isArray(detail))
      message = detail
        .map(
          (item) => `${item.loc?.slice(1).join('.') || 'Input'}: ${item.msg}`,
        )
        .join('; ')
    else if (statusCode < 500 && typeof detail === 'string') message = detail
    if (statusCode >= 500 && path === 'admin/create-user') message = 'Account creation could not be confirmed. Check whether the account exists before trying again.'
    if (statusCode >= 500 && path === 'consultation' && method === 'POST') message = 'The consultation could not be confirmed. Check consultation history before trying again. Your form is preserved.'
    if (statusCode >= 500 && path === 'patients' && method === 'POST') message = 'Patient creation could not be confirmed. Check patient records before trying again.'
    throw createError({ statusCode, message })
  }

  if (signingIn) {
    const credentials = result as { access_token?: string; expired_at?: string }
    const expires = new Date(credentials?.expired_at || '')
    if (
      !credentials?.access_token ||
      !Number.isFinite(expires.getTime()) ||
      expires.getTime() <= Date.now()
    ) {
      throw createError({
        statusCode: 502,
        message: 'The sign-in service returned an invalid response.',
      })
    }
    setCookie(event, cookieName, credentials.access_token, {
      httpOnly: true,
      sameSite: 'strict',
      secure: getRequestURL(event).protocol === 'https:',
      path: '/',
      expires,
    })
    return { success: true }
  }
  if (
    method === 'GET' &&
    (patientDetail
      ? !validPatient(result)
      : consultationDetail
        ? !validConsultation(result)
        : !Array.isArray(result) ||
          !result.every(path === 'diagnosis' ? (value) => validDiagnosis(value) && typeof value.is_valid_for_submission === 'boolean' : path === 'patients' ? validPatient : validConsultation))
  ) {
    throw createError({
      statusCode: 502,
      message: 'The backend has not provided valid data for this feature yet.',
    })
  }
  if (
    path === 'consultation' &&
    method === 'POST' &&
    !validConsultation(result)
  ) {
    throw createError({
      statusCode: 502,
      message:
        'The service did not confirm the saved consultation. Check consultation history before trying again.',
    })
  }
  if (path === 'patients' && method === 'POST' && !validPatient(result)) {
    throw createError({
      statusCode: 502,
      message: 'The service did not confirm the new patient. Check patient records before trying again.',
    })
  }
  if (method === 'POST') setResponseStatus(event, 201)
  if (path === 'admin/create-user') return { success: true }
  return result
})
