<script setup lang="ts">
import type { PatientRecord } from '~/types/clinic'

useHead({ title: 'New patient · ClinicCare' })
async function created(patient: PatientRecord) {
  await navigateTo(`/patients/${patient.id}`)
}
</script>

<template>
  <NuxtLink to="/patients" class="back-link">← Patient list</NuxtLink>
  <div class="page-heading">
    <div>
      <span class="eyebrow">PATIENT RECORDS</span>
      <h1>New patient<span class="heading-dot">.</span></h1>
      <p>Register a patient and open their record.</p>
    </div>
  </div>
  <PatientCreateForm class="consultation-form" @created="created" />
</template>
