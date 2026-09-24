<script setup lang="ts">
import type { Diagnosis } from '~/types/clinic'
useHead({ title: 'New consultation · ClinicCare' })
const { session } = useAuth()
const route = useRoute()
const initialPatientId =
  Number.isInteger(Number(route.query.patient_id)) && Number(route.query.patient_id) > 0
    ? Number(route.query.patient_id)
    : ''
const patientId = ref<number | ''>(initialPatientId)
const notes = ref('')
const diagnoses = ref<Diagnosis[]>([])
const pending = ref(false)
const saved = ref(false)
const error = ref('')
const dirty = computed(
  () =>
    !saved.value &&
    Boolean(
      patientId.value !== initialPatientId ||
      notes.value ||
      diagnoses.value.length,
    ),
)
function selectDiagnosis(item: Diagnosis) {
  if (!diagnoses.value.some((selected) => selected.code === item.code))
    diagnoses.value.push(item)
}
async function submit() {
  if (pending.value || saved.value) return
  error.value = ''
  if (patientId.value === '' || !Number.isInteger(Number(patientId.value)) || Number(patientId.value) < 1) {
    error.value = 'Enter a valid existing patient ID.'
    return
  }
  if (!diagnoses.value.length) {
    error.value = 'Please select at least one diagnosis code.'
    return
  }
  if (!notes.value.trim()) {
    error.value = 'Please enter treatment notes.'
    return
  }
  pending.value = true
  try {
    await $fetch('/api/consultation', {
      method: 'POST',
      body: {
        patient_id: Number(patientId.value),
        diagnosis_codes: diagnoses.value.map((item) => item.code),
        note: notes.value.trim(),
      },
    })
    saved.value = true
    clearNuxtData()
    await navigateTo('/consultations?created=1')
  } catch (cause) {
    error.value = errorMessage(cause)
  } finally {
    pending.value = false
  }
}
function beforeUnload(event: BeforeUnloadEvent) {
  if (dirty.value) {
    event.preventDefault()
    event.returnValue = ''
  }
}
onMounted(() => window.addEventListener('beforeunload', beforeUnload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', beforeUnload))
onBeforeRouteLeave(() => {
  if (!session.value) return true
  if (pending.value && !saved.value) return false
  if (
    dirty.value &&
    !window.confirm(
      'You have unsaved changes. Leave this page and discard them?',
    )
  )
    return false
})
</script>
<template>
  <NuxtLink to="/consultations" class="back-link"
    >← Consultation history</NuxtLink
  >
  <div class="page-heading">
    <div>
      <span class="eyebrow">DOCUMENT A VISIT</span>
      <h1>New consultation<span class="heading-dot">.</span></h1>
      <p>
        Capture patient details, diagnoses, and the next steps in their care.
      </p>
    </div>
    <span class="draft-badge">{{ saved ? 'Saved' : 'Unsaved' }}</span>
  </div>
  <form class="consultation-form" @submit.prevent="submit">
    <fieldset :disabled="pending || saved" class="form-fields">
      <section class="card form-section">
        <div class="section-title">
          <span class="section-number">01</span>
          <div>
            <h2>Patient details</h2>
            <p>Link this visit to an existing patient record.</p>
          </div>
        </div>
        <div class="field">
          <label for="patient-id">Patient ID <span class="required">*</span></label>
          <input id="patient-id" v-model.number="patientId" type="number" required min="1" step="1" placeholder="Enter an existing patient ID" />
          <p class="field-hint">You can find the patient ID in consultation history. Patient registration is not available yet.</p>
        </div>
      </section>
      <section class="card form-section">
        <div class="section-title">
          <span class="section-number">02</span>
          <div>
            <h2>Diagnoses <span class="required">*</span></h2>
            <p>Select one or more relevant ICD-10 codes.</p>
          </div>
        </div>
        <DiagnosisSearch
          :selected="diagnoses"
          selectable
          @select="selectDiagnosis"
        />
        <div v-if="diagnoses.length" class="selected-diagnoses">
          <h3>
            Selected <span class="count-badge">{{ diagnoses.length }}</span>
          </h3>
          <div
            v-for="item in diagnoses"
            :key="item.code"
            class="selected-diagnosis"
          >
            <span class="code-tag">{{ item.code }}</span
            ><span>{{ item.name }}</span
            ><button
              type="button"
              class="icon-button"
              :aria-label="`Remove diagnosis ${item.code}`"
              @click="
                diagnoses = diagnoses.filter((code) => code.code !== item.code)
              "
            >
              <AppIcon name="close" />
            </button>
          </div>
        </div>
      </section>
      <section class="card form-section">
        <div class="section-title">
          <span class="section-number">03</span>
          <div>
            <h2>Treatment notes</h2>
            <p>Document symptoms, assessment, and the treatment plan.</p>
          </div>
        </div>
        <label for="notes"
          >Consultation notes <span class="required">*</span></label
        ><textarea
          id="notes"
          v-model="notes"
          required
          maxlength="10000"
          rows="7"
          placeholder="Symptoms and history…&#10;Clinical assessment…&#10;Treatment plan and follow-up…"
        />
        <div class="field-hint">
          <span>Review the details before saving this record.</span
          ><span>{{ notes.length.toLocaleString('en-GB') }} / 10,000</span>
        </div>
      </section>
    </fieldset>
    <div v-if="error" class="notice error" role="alert">{{ error }}</div>
    <div class="form-actions">
      <span class="muted"><span class="required">*</span> Required fields</span>
      <div>
        <NuxtLink to="/consultations" class="button secondary">Cancel</NuxtLink
        ><button class="button primary" :disabled="pending || saved">
          <AppIcon name="check" />{{
            pending
              ? 'Saving…'
              : saved
                ? 'Consultation saved'
                : 'Save consultation'
          }}
        </button>
      </div>
    </div>
  </form>
</template>
