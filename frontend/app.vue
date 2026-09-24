<script setup lang="ts">
const route = useRoute()
const { session, signOut } = useAuth()
const logoutError = ref('')
const signingOut = ref(false)
const roles: Record<number, string> = {
  1: 'Administrator',
  2: 'Doctor',
  3: 'Nurse',
  4: 'Staff',
}
const roleName = computed(() => roles[session.value?.role || 4] || 'Staff')
async function logout() {
  signingOut.value = true
  logoutError.value = ''
  try {
    await signOut()
  } catch (error) {
    logoutError.value = errorMessage(error)
  } finally {
    signingOut.value = false
  }
}
</script>

<template>
  <NuxtRouteAnnouncer />
  <NuxtLoadingIndicator color="#137c68" />
  <a class="skip-link" href="#main">Skip to main content</a>
  <div v-if="route.path !== '/login'" class="workspace">
    <aside class="sidebar">
      <NuxtLink
        to="/consultations"
        class="brand"
        aria-label="ClinicCare — Home"
      >
        <span class="brand-mark">+</span
        ><span
          >Clinic<span class="brand-light">Care</span
          ><small>MINI EMR</small></span
        >
      </NuxtLink>
      <div class="workspace-label">WORKSPACE</div>
      <nav aria-label="Main navigation" class="main-nav">
        <NuxtLink
          to="/consultations"
          :class="{ active: route.path === '/consultations' }"
          ><AppIcon name="grid" />Consultations</NuxtLink
        >
        <NuxtLink
          to="/consultations/new"
          :class="{ active: route.path === '/consultations/new' }"
          ><AppIcon name="plus" />New consultation</NuxtLink
        >
        <NuxtLink to="/search" :class="{ active: route.path === '/search' }"
          ><AppIcon name="search" />Search records</NuxtLink
        >
        <NuxtLink
          to="/diagnoses"
          :class="{ active: route.path === '/diagnoses' }"
          ><AppIcon name="book" />ICD-10 directory</NuxtLink
        >
        <NuxtLink
          v-if="session?.role === 1"
          to="/admin/users"
          :class="{ active: route.path === '/admin/users' }"
          ><AppIcon name="users" />Create account</NuxtLink
        >
      </nav>
      <div class="sidebar-note">
        <AppIcon name="shield" /><strong>Care starts with understanding</strong>
        <p>Every note is a step toward better, more connected patient care.</p>
      </div>
      <div class="account">
        <span class="avatar">{{ roleName?.slice(0, 1) }}</span>
        <div>
          <strong>{{ roleName }}</strong
          ><small>ClinicCare Workspace</small>
        </div>
        <button
          class="icon-button"
          :disabled="signingOut"
          aria-label="Sign out"
          title="Sign out"
          @click="logout"
        >
          <AppIcon name="logout" />
        </button>
      </div>
      <p v-if="logoutError" class="error-text" role="alert">
        {{ logoutError }}
      </p>
    </aside>
    <div class="workspace-content">
      <header class="topbar">
        <span
          >Clinic <span class="breadcrumb-slash">/</span>
          <strong>Patient care</strong></span
        ><span class="workspace-badge"><span />Internal workspace</span>
      </header>
      <main id="main" class="main-content"><NuxtPage /></main>
      <footer>
        ClinicCare Mini EMR <span>Thoughtful records. Better care.</span>
      </footer>
    </div>
  </div>
  <main v-else id="main"><NuxtPage /></main>
</template>
