<script setup lang="ts">
import type { Consultation, Page, PatientRecord } from '~/types/clinic'

const route = useRoute()
const id = String(route.params.id)
if (!/^[1-9]\d*$/.test(id)) throw createError({ statusCode: 404, message: 'Patient not found.' })

const { data: patient, status: patientStatus, error: patientError, refresh: refreshPatient } =
  await useFetch<PatientRecord>(`/api/patients/${id}`)
const page = ref(1)
const pageSize = 10
const { data: consultations, status: consultationsStatus, error: consultationsError, refresh: refreshConsultations } =
  await useFetch<Page<Consultation>>('/api/consultation', {
    query: computed(() => ({ patient_id: id, page: page.value, page_size: pageSize })),
    default: () => ({ items: [], total: 0, page: 1, page_size: pageSize }),
  })
const pages = computed(() => Math.max(1, Math.ceil(consultations.value.total / pageSize)))

useHead({ title: 'Patient detail · ClinicCare' })
const patientName = computed(() => patient.value
  ? `${patient.value.first_name} ${patient.value.last_name}`
  : 'Patient')
function date(value: string) {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return '—'
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    timeZone: 'Asia/Ho_Chi_Minh',
  }).format(parsed)
}
</script>

<template>
  <NuxtLink to="/patients" class="back-link">← Patient list</NuxtLink>
  <div v-if="patientStatus === 'pending'" class="card empty-state" role="status">
    <span class="spinner" /><h3>Loading patient…</h3>
  </div>
  <ApiFeedback v-else-if="patientError" :error="patientError" @retry="refreshPatient()" />
  <template v-else-if="patient">
    <div class="page-heading">
      <div>
        <span class="eyebrow">PATIENT RECORD</span>
        <h1>{{ patientName }}<span class="heading-dot">.</span></h1>
        <p>Patient #{{ patient.id }} · {{ patient.age }} years · {{ patient.gender === 'NO_PROVIDED' ? 'Gender not provided' : patient.gender.toLowerCase() }}</p>
      </div>
      <NuxtLink :to="`/consultations/new?patient_id=${patient.id}`" class="button primary"><AppIcon name="plus" />New consultation</NuxtLink>
    </div>

    <ApiFeedback v-if="consultationsError" :error="consultationsError" @retry="refreshConsultations()" />
    <section class="card records-card" :aria-busy="consultationsStatus === 'pending'">
      <div class="card-heading">
        <div>
          <h2>Consultations <span v-if="!consultationsError && consultationsStatus !== 'pending'" class="count-badge">{{ consultations.total }}</span></h2>
          <p>Every recorded visit for this patient</p>
        </div>
      </div>
      <div v-if="consultationsStatus === 'pending'" class="empty-state" role="status"><span class="spinner" /><h3>Loading consultations…</h3></div>
      <div v-else-if="consultationsError" class="empty-state"><h3>Consultations are unavailable</h3></div>
      <div v-else-if="!consultations.total" class="empty-state"><h3>No consultations yet</h3><p>Record the first visit for this patient.</p></div>
      <div v-else class="table-scroll" tabindex="0" role="region" aria-label="Patient consultations">
        <table>
          <caption class="sr-only">Consultations for {{ patientName }}</caption>
          <thead><tr><th>CONSULTATION</th><th>VISIT DATE</th><th>DIAGNOSES</th><th>TREATMENT NOTES</th><th><span class="sr-only">Actions</span></th></tr></thead>
          <tbody>
            <tr v-for="item in consultations.items" :key="item.id">
              <td>Consultation #{{ item.id }}</td>
              <td class="nowrap">{{ date(item.created_at) }}</td>
              <td><div class="code-list"><span v-for="diagnosis in item.diagnoses" :key="diagnosis.code" class="code-tag" :title="diagnosis.name">{{ diagnosis.code }}</span></div></td>
              <td><p class="note-preview">{{ item.note }}</p></td>
              <td><NuxtLink :to="`/consultations/${item.id}`" class="text-button nowrap">View consultation</NuxtLink></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="consultations.total" class="table-footer">
        <span>Showing {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, consultations.total) }} of {{ consultations.total }} consultations</span>
        <div class="pagination">
          <button class="button secondary small" :disabled="page <= 1 || consultationsStatus === 'pending'" @click="page--">Previous</button>
          <span>{{ page }} / {{ pages }}</span>
          <button class="button secondary small" :disabled="page >= pages || consultationsStatus === 'pending'" @click="page++">Next</button>
        </div>
      </div>
    </section>
  </template>
</template>
