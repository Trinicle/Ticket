<script lang="ts">
  import github from '$lib/assets/icons/GitHub_Invertocat_Black.svg';
  import send from '$lib/assets/icons/send.svg';
  import folder from '$lib/assets/icons/folder.svg';
</script>

<div class="border rounded-3xl p-2">
  <div
    contenteditable="true"
    class="focus:outline-none mx-2 mt-2 mb-2 min-h-20"
    data-placeholder="Type your task here..."
  ></div>
  <div class="flex justify-between w-full">
    <div class="flex gap-2">
      <button class="btn btn-circle">
        <img src={github} alt="GitHub" />
      </button>
      <button class="btn rounded-full">
        <img src={folder} alt="Folder" />
        <p class="max-w-20 text-ellipsis truncate">Park Place Technologies</p>
      </button>
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
