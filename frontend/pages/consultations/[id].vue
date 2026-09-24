<script setup lang="ts">
import type { Consultation } from '~/types/clinic'

const route = useRoute()
const id = String(route.params.id)
if (!/^[1-9]\d*$/.test(id)) throw createError({ statusCode: 404, message: 'Consultation not found.' })

const { data: consultation, status, error, refresh } =
  await useFetch<Consultation>(`/api/consultation/${id}`)
useHead({ title: 'Consultation detail · ClinicCare' })
const creatorName = computed(() => {
  const creator = consultation.value?.created_by
  return creator
    ? [creator.first_name, creator.last_name].filter(Boolean).join(' ') || creator.email
    : 'Unknown user'
})
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
  <NuxtLink to="/consultations" class="back-link">← Consultation history</NuxtLink>
  <div v-if="status === 'pending'" class="card empty-state" role="status"><span class="spinner" /><h3>Loading consultation…</h3></div>
  <ApiFeedback v-else-if="error" :error="error" @retry="refresh()" />
  <template v-else-if="consultation">
    <div class="page-heading">
      <div>
        <span class="eyebrow">CONSULTATION RECORD</span>
        <h1>Consultation #{{ consultation.id }}<span class="heading-dot">.</span></h1>
        <p>Recorded {{ date(consultation.created_at) }} by {{ creatorName }}</p>
      </div>
      <NuxtLink :to="`/patients/${consultation.patient.id}`" class="button secondary">View patient</NuxtLink>
    </div>
    <div class="detail-sections">
      <section class="card detail-card">
        <h2>Patient</h2>
        <p><NuxtLink :to="`/patients/${consultation.patient.id}`" class="detail-link">{{ consultation.patient.name }}</NuxtLink></p>
        <p class="muted">Patient #{{ consultation.patient.id }} · {{ consultation.patient.age }} years</p>
      </section>
      <section class="card detail-card">
        <h2>Diagnoses</h2>
        <p v-for="diagnosis in consultation.diagnoses" :key="diagnosis.code"><span class="code-tag">{{ diagnosis.code }}</span> {{ diagnosis.name }}</p>
      </section>
      <section class="card detail-card">
        <h2>Treatment notes</h2>
        <p class="full-note">{{ consultation.note }}</p>
      </section>
      <section class="card detail-card">
        <h2>Recorded by</h2>
        <p>{{ creatorName }}</p>
        <p class="muted">{{ consultation.created_by.email }}</p>
      </section>
    </div>
  </template>
</template>
