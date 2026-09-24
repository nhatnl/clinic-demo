<script setup lang="ts">
useHead({ title: 'Sign in · ClinicCare' })
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const pending = ref(false)
const error = ref('')
const { loadSession } = useAuth()
async function submit() {
  pending.value = true
  error.value = ''
  try {
    await $fetch('/api/sign-in', {
      method: 'POST',
      body: { email: email.value.trim(), password: password.value },
    })
    await loadSession()
    await navigateTo('/consultations')
  } catch (cause) {
    error.value = errorMessage(cause)
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <section class="login-story">
      <div class="brand">
        <span class="brand-mark">+</span
        ><span
          >Clinic<span class="brand-light">Care</span
          ><small>MINI EMR</small></span
        >
      </div>
      <div class="story-content">
        <span class="eyebrow">BUILT AROUND YOUR CARE</span>
        <h1>More time<br />for patients.<br /><em>Less paperwork.</em></h1>
        <p>
          One thoughtful workspace to record consultations, find diagnoses, and
          keep the story of care connected.
        </p>
        <div class="story-line"><span /><AppIcon name="plus" /><span /></div>
        <div class="story-features">
          <span><AppIcon name="file" />Connected records</span
          ><span><AppIcon name="book" />ICD-10 directory</span>
        </div>
      </div>
      <small>ClinicCare · Care starts with understanding</small>
    </section>
    <section class="login-form-panel">
      <form class="login-form" @submit.prevent="submit">
        <div class="section-icon"><AppIcon name="shield" /></div>
        <span class="eyebrow">WELCOME BACK</span>
        <h2>Your care workspace<br />starts here</h2>
        <p class="muted">Sign in with the account provided by your clinic.</p>
        <div v-if="error" class="notice error" role="alert">{{ error }}</div>
        <label for="email">Email</label
        ><input
          id="email"
          v-model="email"
          type="email"
          required
          autocomplete="username"
          placeholder="you@clinic.com"
          :disabled="pending"
        />
        <label for="password">Password</label>
        <div class="password-field">
          <input
            id="password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            minlength="6"
            required
            autocomplete="current-password"
            placeholder="Enter your password"
            :disabled="pending"
          /><button
            type="button"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? 'Hide' : 'Show' }}
          </button>
        </div>
        <button class="button primary login-submit" :disabled="pending">
          {{ pending ? 'Signing in…' : 'Sign in' }}<AppIcon name="arrow" />
        </button>
        <p class="login-help">
          Need an account or forgot your password?<br />Please contact your
          clinic administrator.
        </p>
      </form>
      <p class="login-footer">
        <AppIcon name="shield" />For authorized clinic staff only.
      </p>
    </section>
  </div>
</template>
