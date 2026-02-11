<script lang="ts">
  import send from '$lib/assets/icons/send.svg';
  import Source from './Source.svelte';
  import Repo from './Repo.svelte';

  interface Props {
    onSendMessage: (content: string) => void;
    isProcessing?: boolean;
  }

  let { onSendMessage, isProcessing = false }: Props = $props();

  let inputElement: HTMLDivElement | undefined = $state();
  let isDisabled = $derived(isProcessing);

  function handleSend() {
    if (!inputElement || isDisabled) return;

    const content = inputElement.innerText.trim();
    if (!content) return;

    inputElement.innerText = '';
    onSendMessage(content);
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }
</script>

<div class="border border-neutral-300 rounded-3xl p-2 mb-10 shadow-xl">
  <div
    bind:this={inputElement}
    contenteditable={!isDisabled}
    class="focus:outline-hidden focus:ring-2 focus:ring-primary/50 mx-2 mt-2 mb-2 min-h-20 {isDisabled
      ? 'opacity-50 cursor-not-allowed'
      : ''}"
    data-placeholder="Type your task here..."
    onkeydown={handleKeyDown}
  ></div>
  <div class="flex justify-between w-full">
    <div class="flex gap-2">
      <Source />
      <Repo />
    </div>
    <button
      class="btn btn-circle {isDisabled ? 'btn-disabled' : ''}"
      onclick={handleSend}
      disabled={isDisabled}
      aria-label="Send message"
    >
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
