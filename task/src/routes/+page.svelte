<script lang="ts">
  import Input from './Input.svelte';
  import Header from './Header.svelte';

  import type { PageData } from './$types';
  import { api } from '$lib/api';

  export let data: PageData;
</script>

<div class="container mx-auto">
  <Header />
  <div class="mb-20">hi</div>
  <Input />
</div>
