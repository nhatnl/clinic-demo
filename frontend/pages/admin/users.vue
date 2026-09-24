<script setup lang="ts">
useHead({ title: 'Create account · ClinicCare' })
const form = reactive({
  email: '',
  first_name: '',
  last_name: '',
  role: 2,
  password: '',
})
const pending = ref(false)
const error = ref('')
const success = ref('')
async function submit() {
  pending.value = true
  error.value = ''
  success.value = ''
  try {
    await $fetch('/api/admin/create-user', {
      method: 'POST',
      body: {
        ...form,
        email: form.email.trim(),
        first_name: form.first_name.trim() || null,
        last_name: form.last_name.trim() || null,
      },
    })
    success.value = `Account created for ${form.email.trim()}.`
    Object.assign(form, {
      email: '',
      first_name: '',
      last_name: '',
      role: 2,
      password: '',
    })
  } catch (cause) {
    error.value = errorMessage(cause)
  } finally {
    pending.value = false
  }
}
</script>
<template>
  <div class="page-heading">
    <div>
      <span class="eyebrow">CLINIC ADMINISTRATION</span>
      <h1>Create account<span class="heading-dot">.</span></h1>
      <p>Give your team access with the right account and role.</p>
    </div>
    <span class="workspace-badge"><AppIcon name="shield" />Administrator</span>
  </div>
  <form class="narrow-form" @submit.prevent="submit">
    <div v-if="success" class="notice success" role="status">
      <AppIcon name="check" />{{ success }}
    </div>
    <div v-if="error" class="notice error" role="alert">{{ error }}</div>
    <fieldset :disabled="pending" class="card form-section form-fields">
      <div class="section-title">
        <span class="section-number"><AppIcon name="users" /></span>
        <div>
          <h2>Account details</h2>
          <p>The team member will sign in with this email and password.</p>
        </div>
      </div>
      <div class="two-columns">
        <div class="field">
          <label for="last-name">Last name</label
          ><input
            id="last-name"
            v-model="form.last_name"
            maxlength="20"
            autocomplete="off"
            placeholder="Smith"
          />
        </div>
        <div class="field">
          <label for="first-name">First name</label
          ><input
            id="first-name"
            v-model="form.first_name"
            maxlength="20"
            autocomplete="off"
            placeholder="Alex"
          />
        </div>
      </div>
      <div class="field">
        <label for="new-email">Email <span class="required">*</span></label
        ><input
          id="new-email"
          v-model="form.email"
          type="email"
          required
          maxlength="50"
          autocomplete="off"
          placeholder="team@clinic.com"
        />
      </div>
      <div class="field">
        <label for="role">Role <span class="required">*</span></label
        ><select id="role" v-model="form.role">
          <option :value="2">Doctor</option>
          <option :value="3">Nurse</option>
          <option :value="4">Staff</option>
          <option :value="1">Administrator</option>
        </select>
      </div>
      <div class="field">
        <label for="new-password"
          >Password <span class="required">*</span></label
        ><input
          id="new-password"
          v-model="form.password"
          type="password"
          required
          minlength="6"
          maxlength="20"
          pattern="(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])\S{6,20}"
          autocomplete="new-password"
          aria-describedby="password-help"
        />
        <p id="password-help" class="field-hint">
          6–20 characters, including uppercase, lowercase, a number, and a
          special character. No spaces.
        </p>
      </div>
      <div class="form-actions">
        <span class="muted"
          ><span class="required">*</span> Required fields</span
        ><button class="button primary" :disabled="pending">
          <AppIcon name="plus" />{{ pending ? 'Creating…' : 'Create account' }}
        </button>
      </div>
    </fieldset>
  </form>
</template>
