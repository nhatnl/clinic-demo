<script setup lang="ts">
useHead({ title: 'ICD-10 directory · ClinicCare' })
</script>
<template>
  <div class="page-heading">
    <div>
      <span class="eyebrow">DIAGNOSIS REFERENCE</span>
      <h1>ICD-10 directory<span class="heading-dot">.</span></h1>
      <p>Find the right diagnosis code for accurate consultation records.</p>
    </div>
    <span class="page-heading-icon"><AppIcon name="book" /></span>
  </div>
  <section class="card form-section">
    <div class="section-title">
      <span class="section-number"><AppIcon name="book" /></span>
      <div>
        <h2>Diagnosis library</h2>
        <p>Browse the diagnosis directory provided by your clinic.</p>
      </div>
    </div>
    <DiagnosisSearch />
  </section>
  <p class="page-note">
    Use category codes to explore and billable codes to record a consultation.
  </p>
</template>
