<script setup lang="ts">
import type { Page, PatientRecord } from '~/types/clinic'

useHead({ title: 'Patients · ClinicCare' })
const page = ref(1)
const pageSize = 10
const { data: patients, status, error, refresh } = await useFetch<Page<PatientRecord>>('/api/patients', {
  query: computed(() => ({ page: page.value, page_size: pageSize })),
  default: () => ({ items: [], total: 0, page: 1, page_size: pageSize }),
})
const pages = computed(() => Math.max(1, Math.ceil(patients.value.total / pageSize)))
</script>

<template>
  <div class="page-heading">
    <div>
      <span class="eyebrow">PATIENT RECORDS</span>
      <h1>Patients<span class="heading-dot">.</span></h1>
      <p>Browse patient records and their consultations.</p>
    </div>
    <NuxtLink to="/patients/new" class="button primary"><AppIcon name="plus" />New patient</NuxtLink>
  </div>

  <ApiFeedback v-if="error" :error="error" @retry="refresh()" />
  <section class="card records-card" :aria-busy="status === 'pending'">
    <div class="card-heading">
      <div>
        <h2>Patient list <span v-if="!error && status !== 'pending'" class="count-badge">{{ patients.total }}</span></h2>
        <p>Registered patients</p>
      </div>
    </div>
    <div v-if="status === 'pending'" class="empty-state" role="status"><span class="spinner" /><h3>Loading patients…</h3></div>
    <div v-else-if="error" class="empty-state"><h3>Patients are unavailable</h3></div>
    <div v-else-if="!patients.total" class="empty-state"><h3>No patients yet</h3><p>Create a patient to get started.</p></div>
    <div v-else class="table-scroll" tabindex="0" role="region" aria-label="Patient list">
      <table>
        <caption class="sr-only">Registered patients</caption>
        <thead><tr><th>PATIENT</th><th>AGE</th><th>GENDER</th><th><span class="sr-only">Actions</span></th></tr></thead>
        <tbody>
          <tr v-for="patient in patients.items" :key="patient.id">
            <td><NuxtLink :to="`/patients/${patient.id}`" class="text-button">{{ patient.first_name }} {{ patient.last_name }}</NuxtLink></td>
            <td>{{ patient.age }}</td>
            <td>{{ patient.gender === 'NO_PROVIDED' ? 'Not provided' : patient.gender.toLowerCase() }}</td>
            <td><NuxtLink :to="`/patients/${patient.id}`" class="text-button nowrap">View patient</NuxtLink></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="patients.total" class="table-footer">
      <span>Showing {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, patients.total) }} of {{ patients.total }} patients</span>
      <div class="pagination">
        <button class="button secondary small" :disabled="page <= 1 || status === 'pending'" @click="page--">Previous</button>
        <span>{{ page }} / {{ pages }}</span>
        <button class="button secondary small" :disabled="page >= pages || status === 'pending'" @click="page++">Next</button>
      </div>
    </div>
  </section>
</template>
