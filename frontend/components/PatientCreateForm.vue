<script setup lang="ts">
import type { PatientRecord } from '~/types/clinic'

const emit = defineEmits<{ created: [patient: PatientRecord] }>()
const firstName = ref('')
const lastName = ref('')
const age = ref<number | ''>('')
const gender = ref('NO_PROVIDED')
const pending = ref(false)
const saved = ref(false)
const error = ref('')

async function submit() {
  if (pending.value || saved.value) return
  error.value = ''
  if (firstName.value.trim().length < 3 || lastName.value.trim().length < 3) {
    error.value = 'First and last names must each have at least 3 characters.'
    return
  }
  if (age.value === '' || !Number.isInteger(Number(age.value)) || Number(age.value) < 0 || Number(age.value) > 150) {
    error.value = 'Enter an age from 0 to 150.'
    return
  }
  pending.value = true
  try {
    const patient = await $fetch<PatientRecord>('/api/patients', {
      method: 'POST',
      body: {
        first_name: firstName.value.trim(),
        last_name: lastName.value.trim(),
        age: Number(age.value),
        gender: gender.value,
      },
    })
    saved.value = true
    emit('created', patient)
  } catch (cause) {
    error.value = errorMessage(cause)
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <form class="card form-section patient-create-form" @submit.prevent="submit">
    <div class="section-title">
      <span class="section-number"><AppIcon name="users" /></span>
      <div><h2>New patient</h2><p>Register a patient before recording a consultation.</p></div>
    </div>
    <fieldset class="form-fields" :disabled="pending || saved">
      <div class="two-columns">
        <div class="field">
          <label for="new-patient-first-name">First name <span class="required">*</span></label>
          <input id="new-patient-first-name" v-model="firstName" required minlength="3" maxlength="20" autocomplete="given-name" />
        </div>
        <div class="field">
          <label for="new-patient-last-name">Last name <span class="required">*</span></label>
          <input id="new-patient-last-name" v-model="lastName" required minlength="3" maxlength="20" autocomplete="family-name" />
        </div>
      </div>
      <div class="two-columns patient-create-secondary">
        <div class="field">
          <label for="new-patient-age">Age <span class="required">*</span></label>
          <input id="new-patient-age" v-model.number="age" type="number" required min="0" max="150" step="1" />
        </div>
        <div class="field">
          <label for="new-patient-gender">Gender</label>
          <select id="new-patient-gender" v-model="gender">
            <option value="NO_PROVIDED">Not provided</option>
            <option value="MALE">Male</option>
            <option value="FEMALE">Female</option>
          </select>
        </div>
      </div>
    </fieldset>
    <div v-if="error" class="notice error" role="alert">{{ error }}</div>
    <div class="form-actions patient-create-actions">
      <span class="muted"><span class="required">*</span> Required fields</span>
      <button class="button primary" :disabled="pending || saved"><AppIcon name="check" />{{ pending ? 'Creating…' : saved ? 'Patient created' : 'Create patient' }}</button>
    </div>
  </form>
</template>
