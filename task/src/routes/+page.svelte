<script lang="ts">
  import Input from './Input.svelte';
  import Header from './Header.svelte';

  interface Message {
    from: 'user' | 'model';
    content: string;
  }

  let chatContent = $state<Message[]>([]);
</script>

<Header />
<div class="w-5xl mx-auto h-screen flex flex-col">
  <div class="flex flex-col w-full flex-1">
    <div class="grow overflow-auto my-10 w-full">
      {#each chatContent as message}
        {#if message.from === 'model'}
          <div class="w-full mb-2">
            {message.content}
          </div>
        {:else}
          <div
            class="bg-primary rounded-2xl px-4 py-3 ml-auto w-fit max-w-lg mb-2 leading-5"
          >
            {message.content}
          </div>
        {/if}
      {/each}
    </div>
    <Input />
  </div>
</div>
