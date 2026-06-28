<script setup>
import NavigationComponent from "@/components/NavigationComponent.vue";
import FooterComponent from "@/components/FooterComponent.vue";
</script>

<template>
  <div class="container text-center">
    <navigation-component></navigation-component>
    <router-view></router-view>
    <footer-component></footer-component>
  </div>
</template>

<style scoped></style>
