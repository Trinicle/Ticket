<script lang="ts">
  import github from '$lib/assets/icons/GitHub_Invertocat_Black.svg';
  import edit from '$lib/assets/icons/edit.svg';
</script>

<button
  class="btn btn-circle"
  style="anchor-name:--anchor-source"
  popovertarget="source-popover"
>
  <img src={github} alt="GitHub" />
</button>

<ul
  class="dropdown dropdown-top menu w-52 rounded-box bg-base-100 shadow-sm"
  popover
  id="source-popover"
  style="position-anchor:--anchor-source"
>
  <li class="py-1.5 px-3">Sources</li>
  <li><a class="menu-active">GitHub</a></li>
  <li><a>GitLab</a></li>
  <li><a>Azure DevOps</a></li>
</ul>
