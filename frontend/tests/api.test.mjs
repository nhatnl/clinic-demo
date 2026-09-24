import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import { createServer } from 'node:http'
import { setTimeout as delay } from 'node:timers/promises'
import test from 'node:test'

// A test-only upstream. Production never falls back to mock patient records.
test(
  'session, API bridge, route guards, and backend failures',
  { timeout: 30000 },
  async () => {
    const claims = Buffer.from(
      JSON.stringify({
        sub: '42',
        role: 1,
        exp: Math.floor(Date.now() / 1000) + 3600,
      }),
    ).toString('base64url')
    const token = `test.${claims}.test-signature`
    const diagnosis = {
      code: 'A00.0',
      name: 'Cholera',
      is_valid_for_submission: true,
    }
    const consultation = {
      id: 1,
      patient: { id: 7, name: 'Alex Smith', age: 32 },
      created_by: {
        id: 42,
        email: 'doctor@clinic.test',
        first_name: 'Alex',
        last_name: 'Doctor',
        role: 2,
      },
      note: 'Follow up in one week.',
      diagnoses: [{ code: diagnosis.code, name: diagnosis.name, description: null }],
      created_at: '2026-09-24T08:00:00Z',
      updated_at: '2026-09-24T08:00:00Z',
    }
    const patient = {
      id: 7,
      first_name: 'Alex',
      last_name: 'Smith',
      age: 32,
      gender: 'MALE',
    }
    let mode = 'ok'
    const requests = []
    const upstream = createServer(async (req, res) => {
      const chunks = []
      for await (const chunk of req) chunks.push(chunk)
      const body = chunks.length ? JSON.parse(Buffer.concat(chunks)) : undefined
      requests.push({
        url: req.url,
        method: req.method,
        authorization: req.headers.authorization,
        body,
      })
      res.setHeader('Content-Type', 'application/json')
      if (mode === 'offline') {
        res.writeHead(500)
        res.end(JSON.stringify({ detail: 'Private database details' }))
        return
      }
      if (mode === 'missing') {
        res.writeHead(404)
        res.end(JSON.stringify({ detail: 'Not Found' }))
        return
      }
      if (mode === 'expired') {
        res.writeHead(401)
        res.end(JSON.stringify({ detail: 'Unauthorized' }))
        return
      }
      if (mode === 'invalid') {
        res.writeHead(422)
        res.end(
          JSON.stringify({
            detail: [{ loc: ['body', 'email'], msg: 'Invalid email' }],
          }),
        )
        return
      }
      if (req.url === '/auth/sign-in') {
        if (body.password !== 'Valid123!') {
          res.writeHead(401)
          res.end('{}')
          return
        }
        res.end(
          JSON.stringify({
            access_token: token,
            expired_at: new Date(Date.now() + 3600000).toISOString(),
          }),
        )
        return
      }
      if (req.headers.authorization !== `Bearer ${token}`) {
        res.writeHead(401)
        res.end('{}')
        return
      }
      if (req.url.startsWith('/diagnosis/')) {
        res.end(JSON.stringify(mode === 'stub' ? null : [diagnosis]))
        return
      }
      if (req.url === '/patients/7') {
        res.end(JSON.stringify(patient))
        return
      }
      if (req.url === '/patients/' && req.method === 'GET') {
        res.end(JSON.stringify([patient]))
        return
      }
      if (req.url === '/patients/' && req.method === 'POST') {
        res.writeHead(201)
        res.end(JSON.stringify(mode === 'stub' ? null : patient))
        return
      }
      if (req.url === '/consultation/1') {
        res.end(JSON.stringify(consultation))
        return
      }
      if (req.url.startsWith('/consultation')) {
        if (mode === 'missing-patient' && req.method === 'POST') {
          res.writeHead(404)
          res.end(JSON.stringify({ detail: 'Patient not found' }))
          return
        }
        if (req.method === 'POST') res.writeHead(201)
        res.end(
          JSON.stringify(req.method === 'POST' ? consultation : [consultation]),
        )
        return
      }
      if (req.url === '/admin/create-user') {
        res.writeHead(201)
        res.end(
          JSON.stringify({
            id: 2,
            email: 'new@clinic.test',
            role: 2,
            first_name: null,
            last_name: null,
            password_hash: 'must-never-reach-the-browser',
          }),
        )
        return
      }
      res.writeHead(404)
      res.end('{}')
    })
    upstream.listen(0, '127.0.0.1')
    await once(upstream, 'listening')
    const portProbe = createServer()
    portProbe.listen(0, '127.0.0.1')
    await once(portProbe, 'listening')
    const appPort = portProbe.address().port
    await new Promise((resolve) => portProbe.close(resolve))
    const app = spawn(process.execPath, ['.output/server/index.mjs'], {
      cwd: new URL('..', import.meta.url),
      env: {
        ...process.env,
        PORT: String(appPort),
        NITRO_PORT: String(appPort),
        NITRO_HOST: '127.0.0.1',
        NUXT_API_BASE: `http://127.0.0.1:${upstream.address().port}`,
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    let output = ''
    let errors = ''
    app.stdout.on('data', (chunk) => {
      output += chunk
    })
    app.stderr.on('data', (chunk) => {
      errors += chunk
    })
    try {
      for (
        let i = 0;
        i < 100 && !output.match(/http:\/\/127\.0\.0\.1:\d+/);
        i++
      ) {
        if (app.exitCode !== null) throw new Error(`Nuxt exited: ${errors}`)
        await delay(50)
      }
      const base = output.match(/http:\/\/127\.0\.0\.1:\d+/)?.[0]
      assert.ok(base, `Nuxt did not start: ${output} ${errors}`)
      const request = (path, options = {}) =>
        fetch(`${base}${path}`, { redirect: 'manual', ...options })
      const post = (path, body, cookie, extraHeaders = {}) =>
        request(path, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(cookie ? { Cookie: cookie } : {}),
            ...extraHeaders,
          },
          body: JSON.stringify(body),
        })
      assert.equal((await request('/api/session')).status, 200)
      assert.deepEqual(await (await request('/api/session')).json(), {
        user: null,
      })
      assert.equal((await request('/api/consultation')).status, 401)
      assert.equal(
        (await request('/consultations')).headers.get('location'),
        '/login',
      )
      const loginPage = await request('/login')
      assert.match(await loginPage.text(), /Your care workspace/)
      assert.equal(
        (
          await post('/api/sign-in', {
            email: 'admin@clinic.test',
            password: 'wrong',
          })
        ).status,
        401,
      )
      const login = await post('/api/sign-in', {
        email: 'admin@clinic.test',
        password: 'Valid123!',
      })
      assert.equal(login.status, 200)
      const setCookie = login.headers.get('set-cookie')
      assert.match(setCookie, /HttpOnly/i)
      assert.match(setCookie, /SameSite=Strict/i)
      const cookie = setCookie.split(';')[0]
      assert.deepEqual(await login.json(), { success: true })
      assert.deepEqual(
        await (
          await request('/api/session', { headers: { Cookie: cookie } })
        ).json(),
        { user: { id: '42', role: 1 } },
      )
      const headers = { Cookie: cookie }
      for (const path of [
        '/consultations',
        '/consultations/new',
        '/patients',
        '/patients/new',
        '/patients/7',
        '/consultations/1',
        '/search',
        '/diagnoses',
        '/admin/users',
      ]) {
        const page = await request(path, { headers })
        assert.equal(page.status, 200, path)
        assert.doesNotMatch(
          await page.text(),
          /must-never-reach-the-browser|test-signature/,
        )
      }
      const patientsPage = await (await request('/patients', { headers })).text()
      assert.match(patientsPage, /Alex Smith/)
      assert.match(patientsPage, /List consultations/)
      assert.match(patientsPage, /List patients/)
      assert.match(patientsPage, /href="\/patients\/7"/)
      const patientPage = await (await request('/patients/7', { headers })).text()
      assert.match(patientPage, /Alex Smith/)
      assert.match(patientPage, /\/consultations\/1/)
      const newPatientPage = await (await request('/patients/new', { headers })).text()
      assert.match(newPatientPage, /First name/)
      const newConsultationPage = await (await request('/consultations/new', { headers })).text()
      assert.match(newConsultationPage, /Search by first or last name/)
      assert.match(newConsultationPage, /role="combobox"/)
      assert.match(newConsultationPage, /New patient/)
      assert.ok(requests.some((item) => item.url === '/consultation?patient_id=7'))
      const consultationPage = await (await request('/consultations/1', { headers })).text()
      assert.match(consultationPage, /Follow up in one week/)
      assert.match(consultationPage, /Alex Doctor/)
      assert.match(consultationPage, /\/patients\/7/)
      assert.deepEqual(
        await (await request('/api/diagnosis?search=A00', { headers })).json(),
        [diagnosis],
      )
      assert.equal(requests.at(-1).url, '/diagnosis/?search=A00')
      await request('/api/consultation?patient=Alex&diagnosis_code=A00.0', {
        headers,
      })
      assert.equal(
        requests.at(-1).url,
        '/consultation?patient=Alex&diagnosis_code=A00.0',
      )
      assert.deepEqual(
        await (await request('/api/patients/7', { headers })).json(),
        patient,
      )
      assert.deepEqual(
        await (await request('/api/patients', { headers })).json(),
        [patient],
      )
      assert.equal(requests.at(-1).url, '/patients/')
      assert.deepEqual(
        await (await request('/api/consultation/1', { headers })).json(),
        consultation,
      )
      await request('/api/consultation?patient_id=7', { headers })
      assert.equal(requests.at(-1).url, '/consultation?patient_id=7')
      assert.equal((await request('/api/patients/not-an-id', { headers })).status, 404)
      const patientInput = {
        first_name: 'Alex',
        last_name: 'Smith',
        age: 32,
        gender: 'MALE',
      }
      const patientCreated = await post('/api/patients', patientInput, cookie)
      assert.equal(patientCreated.status, 201)
      assert.deepEqual(await patientCreated.json(), patient)
      assert.deepEqual(requests.at(-1).body, patientInput)
      const input = {
        patient_id: 7,
        diagnosis_codes: ['A00.0'],
        note: 'Follow up in one week.',
      }
      assert.equal((await post('/api/consultation', input, cookie)).status, 201)
      assert.deepEqual(requests.at(-1).body, input)
      mode = 'missing-patient'
      const missingPatient = await post('/api/consultation', input, cookie)
      assert.equal(missingPatient.status, 404)
      assert.equal((await missingPatient.json()).message, 'Patient not found')
      mode = 'ok'
      const admin = await post(
        '/api/admin/create-user',
        { email: 'new@clinic.test' },
        cookie,
      )
      assert.equal(admin.status, 201)
      assert.deepEqual(await admin.json(), { success: true })
      assert.equal(
        (
          await post('/api/consultation', input, cookie, {
            Origin: 'https://other.example',
          })
        ).status,
        403,
      )
      assert.equal(
        (await request('/api/consultation', { method: 'POST', headers }))
          .status,
        415,
      )
      assert.equal(
        (await request('/api/arbitrary-path', { headers })).status,
        404,
      )
      mode = 'stub'
      assert.equal(
        (await request('/api/diagnosis?search=A00', { headers })).status,
        502,
      )
      mode = 'missing'
      assert.match(
        (await (await request('/api/consultation', { headers })).json())
          .message,
        /not yet available/,
      )
      mode = 'invalid'
      assert.match(
        (await (await post('/api/admin/create-user', {}, cookie)).json())
          .message,
        /email: Invalid email/,
      )
      mode = 'offline'
      const failure = await request('/api/consultation', { headers })
      assert.equal(failure.status, 500)
      assert.doesNotMatch(await failure.text(), /Private database/)
    assert.match((await (await post('/api/admin/create-user', {}, cookie)).json()).message, /Check whether the account exists/)
    assert.match((await (await post('/api/consultation', input, cookie)).json()).message, /Check consultation history/)
      mode = 'expired'
      const expired = await request('/api/consultation', { headers })
      assert.equal(expired.status, 401)
      assert.match(expired.headers.get('set-cookie'), /Max-Age=0/i)
      assert.deepEqual(
        await (
          await request('/api/session', {
            headers: { Cookie: 'clinic_session=malformed' },
          })
        ).json(),
        { user: null },
      )
      const logout = await post('/api/sign-out', {}, cookie)
      assert.match(logout.headers.get('set-cookie'), /Max-Age=0/i)
    } finally {
      const exited = once(app, 'exit')
      app.kill('SIGTERM')
      await Promise.race([exited, delay(2000)])
      if (app.exitCode === null) {
        app.kill('SIGKILL')
        await exited
      }
      upstream.closeAllConnections()
      await new Promise((resolve) => upstream.close(resolve))
    }
  },
)
