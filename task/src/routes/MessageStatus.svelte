<script lang="ts">
  interface Props {
    message?: string;
  }

  let { message = 'Processing...' }: Props = $props();
</script>

<div class="flex items-center gap-2 text-base-content/70 px-4 py-3">
  <span class="text-sm">{message}</span>
  <div class="flex gap-1">
    <span class="typing-dot" style="animation-delay: 0s"></span>
    <span class="typing-dot" style="animation-delay: 0.2s"></span>
    <span class="typing-dot" style="animation-delay: 0.4s"></span>
  </div>
</div>

<style>
  .typing-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: currentColor;
    display: inline-block;
    animation: typing 1.4s infinite ease-in-out;
  }

  @keyframes typing {
    0%,
    60%,
    100% {
      transform: translateY(0);
      opacity: 0.7;
    }
    30% {
      transform: translateY(-8px);
      opacity: 1;
    }
  }
</style>
