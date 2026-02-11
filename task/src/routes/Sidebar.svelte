<script lang="ts">
  import type { Conversation } from '$lib/data/conversations';
  import { formatTimestamp } from '$lib/data/conversations';

  interface Props {
    conversations: Conversation[];
    selectedConversationId: string | null;
    onSelectConversation: (id: string) => void;
    onCreateNew: () => void;
  }

  let { conversations, selectedConversationId, onSelectConversation, onCreateNew }: Props = $props();

  function handleConversationClick(id: string) {
    onSelectConversation(id);
  }

  function handleNewChat() {
    onCreateNew();
  }
</script>

<aside class="flex min-h-full flex-col bg-base-200 w-80 is-drawer-close:w-16 is-drawer-close:overflow-visible">
  <!-- Toggle Button (Always Visible) -->
  <div class="p-4 flex items-center justify-center min-h-[64px]">
    <label
      for="sidebar-drawer"
      class="btn btn-ghost btn-circle drawer-button"
      aria-label="toggle sidebar"
    >
      <!-- Hamburger menu icon -->
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </label>
  </div>

  <!-- New Chat Button -->
  <div class="p-4 is-drawer-close:hidden">
    <button class="btn btn-primary w-full" onclick={handleNewChat}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
      <span class="is-drawer-close:hidden">New Chat</span>
    </button>
  </div>

  <!-- Icon-only New Chat Button when collapsed -->
  <div class="p-2 is-drawer-open:hidden">
    <button
      class="btn btn-ghost btn-circle w-full tooltip tooltip-right"
      data-tip="New Chat"
      onclick={handleNewChat}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
    </button>
  </div>

  <!-- Conversation List (Hidden when drawer is closed) -->
  <div class="flex-1 overflow-y-auto is-drawer-close:hidden">
    {#if conversations.length === 0}
      <div class="p-4 text-center text-base-content/60">
        <p>No conversations yet</p>
        <p class="text-sm mt-2">Start a new chat to begin</p>
      </div>
    {:else}
      <ul class="menu p-2">
        {#each conversations as conversation (conversation.id)}
          <li>
            <button
              class="flex flex-col items-start gap-1 p-3 rounded-lg hover:bg-base-300 transition-colors {selectedConversationId ===
              conversation.id
                ? 'bg-base-300'
                : ''}"
              onclick={() => handleConversationClick(conversation.id)}
            >
              <div class="flex items-center justify-between w-full">
                <span class="font-medium text-sm truncate max-w-full" title={conversation.title}>
                  {conversation.title}
                </span>
              </div>
              <span class="text-xs text-base-content/60 line-clamp-1 w-full" title={conversation.lastMessage}>
                {conversation.lastMessage}
              </span>
              <span class="text-xs text-base-content/40 mt-1">
                {formatTimestamp(conversation.timestamp)}
              </span>
            </button>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</aside>

<style>
  .line-clamp-1 {
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
