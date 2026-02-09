<script lang="ts">
  import send from '$lib/assets/icons/send.svg';
  import Source from './Source.svelte';
  import Repo from './Repo.svelte';
</script>

<div class="border border-neutral-300 rounded-3xl p-2 mb-10 shadow-xl">
  <div
    contenteditable="true"
    class="focus:outline-none mx-2 mt-2 mb-2 min-h-20"
    data-placeholder="Type your task here..."
  ></div>
  <div class="flex justify-between w-full">
    <div class="flex gap-2">
      <Source />
      <Repo />
    </div>
    <button class="btn btn-circle">
      <img src={send} alt="Send" class="mt-0.5 mr-0.5" height="20" width="20" />
    </button>
  </div>
</div>

<style>
  [contenteditable]:empty:before {
    content: attr(data-placeholder);
    color: #888;
    pointer-events: none;
    display: block;
  }

  [contenteditable]:focus:empty:before {
    content: none;
  }
</style>
