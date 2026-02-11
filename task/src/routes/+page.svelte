<script lang="ts">
  import Input from './Input.svelte';
  import Header from './Header.svelte';
  import Sidebar from './Sidebar.svelte';
  import MessageStatus from './MessageStatus.svelte';
  import type { ChatMessage, Conversation } from '$lib/data/conversations';
  import {
    mockConversations,
    mockMessages,
    generateConversationId,
    generateMessageId
  } from '$lib/data/conversations';

  let conversations = $state<Conversation[]>([...mockConversations]);
  let currentConversationId = $state<string | null>(null);
  let chatContent = $state<ChatMessage[]>([]);
  let isProcessing = $state(false);
  let chatContainer: HTMLDivElement | undefined = $state();

  $effect(() => {
    if (conversations.length > 0 && currentConversationId === null) {
      currentConversationId = conversations[0].id;
      loadConversationMessages(currentConversationId);
    }
  });

  function loadConversationMessages(conversationId: string) {
    const messages = mockMessages[conversationId] || [];
    chatContent = [...messages];
    scrollToBottom();
  }

  function scrollToBottom() {
    if (chatContainer) {
      setTimeout(() => {
        chatContainer?.scrollTo({
          top: chatContainer.scrollHeight,
          behavior: 'smooth'
        });
      }, 0);
    }
  }

  function handleSelectConversation(id: string) {
    currentConversationId = id;
    loadConversationMessages(id);
    isProcessing = false;
  }

  function handleCreateNew() {
    const newId = generateConversationId();
    const newConversation: Conversation = {
      id: newId,
      title: 'New Chat',
      lastMessage: '',
      timestamp: new Date(),
      messageCount: 0
    };
    conversations = [newConversation, ...conversations];
    currentConversationId = newId;
    chatContent = [];
    isProcessing = false;
  }

  async function handleSendMessage(content: string) {
    if (!currentConversationId || !content.trim()) return;

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: generateMessageId(),
      from: 'user',
      content: content.trim(),
      timestamp: new Date(),
      status: 'complete'
    };

    chatContent = [...chatContent, userMessage];
    isProcessing = true;
    scrollToBottom();

    updateConversationMetadata(currentConversationId, content.trim());

    await new Promise((resolve) => setTimeout(resolve, 1500 + Math.random() * 1000));

    const modelResponse: ChatMessage = {
      id: generateMessageId(),
      from: 'model',
      content: generateMockResponse(content),
      timestamp: new Date(),
      status: 'complete'
    };

    chatContent = [...chatContent, modelResponse];
    isProcessing = false;
    scrollToBottom();

    updateConversationMetadata(currentConversationId, modelResponse.content);
  }

  function updateConversationMetadata(conversationId: string, lastMessage: string) {
    conversations = conversations.map((conv) => {
      if (conv.id === conversationId) {
        return {
          ...conv,
          lastMessage: lastMessage.length > 60 ? lastMessage.substring(0, 60) + '...' : lastMessage,
          timestamp: new Date(),
          messageCount: conv.messageCount + 1,
          title: conv.title === 'New Chat' && chatContent.length === 1
            ? lastMessage.length > 30 ? lastMessage.substring(0, 30) + '...' : lastMessage
            : conv.title
        };
      }
      return conv;
    });
  }

  function generateMockResponse(userMessage: string): string {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('issue') || lowerMessage.includes('bug')) {
      return 'I can help you with issues. Would you like me to:\n\n1. List open issues\n2. Search for specific issues\n3. Create a new issue\n4. Get details about a particular issue\n\nWhat would you like to do?';
    } else if (lowerMessage.includes('stat') || lowerMessage.includes('metric') || lowerMessage.includes('velocity')) {
      return 'I can provide repository statistics and team velocity metrics. Let me fetch the latest data for you...';
    } else if (lowerMessage.includes('pull request') || lowerMessage.includes('pr')) {
      return 'I can help you with pull requests. Would you like me to:\n\n1. List open pull requests\n2. Review a specific PR\n3. Get PR details\n\nWhat would you like to do?';
    } else if (lowerMessage.includes('label')) {
      return 'I can help you manage labels. Would you like to:\n\n1. List all labels\n2. Create a new label\n3. Update existing labels\n4. Get labels for a specific issue\n\nWhat would you like to do?';
    } else {
      return `I understand you're asking about "${userMessage}". Let me help you with that. Could you provide more details about what you'd like me to do?`;
    }
  }

  function formatMessageTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
</script>

<Header />
<div class="drawer lg:drawer-open">
  <input id="sidebar-drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col h-screen overflow-hidden">
    <div bind:this={chatContainer} class="flex-1 overflow-y-auto bg-base-100">
      <div class="max-w-4xl mx-auto px-4 py-6">
        {#if chatContent.length === 0}
          <div class="flex items-center justify-center h-full text-base-content/60">
            <div class="text-center">
              <p class="text-lg font-medium mb-2">Start a new conversation</p>
              <p class="text-sm">Type a message below to begin chatting</p>
            </div>
          </div>
        {:else}
          <div class="space-y-4">
            {#each chatContent as message (message.id)}
              {#if message.from === 'user'}
                <div class="flex justify-end">
                  <div class="bg-primary text-primary-content rounded-2xl px-4 py-3 max-w-lg leading-5">
                    <p class="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              {:else}
                <div class="w-full">
                  <div class="px-4 py-3 leading-5">
                    <p class="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              {/if}
            {/each}
            {#if isProcessing}
              <MessageStatus />
            {/if}
          </div>
        {/if}
      </div>
    </div>
    <div class="bg-base-100">
      <div class="max-w-4xl mx-auto">
        <Input onSendMessage={handleSendMessage} {isProcessing} />
      </div>
    </div>
  </div>
  <div class="drawer-side">
    <label for="sidebar-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
    <Sidebar
      conversations={conversations}
      selectedConversationId={currentConversationId}
      onSelectConversation={handleSelectConversation}
      onCreateNew={handleCreateNew}
    />
  </div>
</div>
