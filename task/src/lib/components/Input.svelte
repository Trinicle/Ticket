<script lang="ts">
  import eyeOpen from '$lib/assets/icons/eye_open.svg';
  import eyeClosed from '$lib/assets/icons/eye_closed.svg';

  interface LinkText {
    text: string;
    link: string;
  }

  interface InputProps {
    label?: string;
    leftIcon?: string;
    rightIcon?: string;
    placeholder?: string;
    id?: string;
    name?: string;
    type?:
      | 'text'
      | 'password'
      | 'email'
      | 'number'
      | 'tel'
      | 'url'
      | 'search'
      | 'date'
      | 'time'
      | 'datetime-local'
      | 'month'
      | 'week';
    linkText?: LinkText;

    // Value binding
    value?: string;

    // Common events
    oninput?: (event: Event) => void;
    onchange?: (event: Event) => void;
    onfocus?: (event: FocusEvent) => void;
    onblur?: (event: FocusEvent) => void;
    onkeydown?: (event: KeyboardEvent) => void;
    onkeyup?: (event: KeyboardEvent) => void;
    onclick?: (event: MouseEvent) => void;

    // Clipboard events
    onpaste?: (event: ClipboardEvent) => void;
    oncut?: (event: ClipboardEvent) => void;

    // Validation and attributes
    required?: boolean;
    disabled?: boolean;
    readonly?: boolean;
    autocomplete?:
      | 'off'
      | 'on'
      | 'name'
      | 'email'
      | 'username'
      | 'new-password'
      | 'current-password'
      | 'tel'
      | 'url';
    min?: string | number;
    max?: string | number;
    minlength?: number;
    maxlength?: number;
    pattern?: string;
  }

  let {
    label,
    leftIcon,
    rightIcon,
    placeholder,
    id,
    name,
    type = 'text',
    linkText,
    value,
    oninput,
    onchange,
    onfocus,
    onblur,
    onkeydown,
    onkeyup,
    onclick,
    onpaste,
    oncut,
    required,
    disabled,
    readonly,
    autocomplete,
    min,
    max,
    minlength,
    maxlength,
    pattern,
  }: InputProps = $props();

  let showPassword = $state(false);

  let inputType = $derived(type === 'password' && showPassword ? 'text' : type);

  function togglePassword() {
    showPassword = !showPassword;
  }
</script>

<fieldset class="fieldset">
  <div class="w-full flex">
    {#if label}
      <legend class="fieldset-legend text-sm pb-0.5 pt-0">{label}</legend>
    {/if}
    {#if linkText}
      <a
        href={linkText.link}
        class="fieldset-legend text-xs pb-0.5 pt-0 ml-auto"
      >
        {linkText.text}
      </a>
    {/if}
  </div>

  <label class="input w-full">
    {#if leftIcon}
      <img src={leftIcon} alt="Left icon" class="h-[1em]" />
    {/if}
    <input
      type={inputType}
      bind:value
      {placeholder}
      {id}
      {name}
      {required}
      {disabled}
      {readonly}
      {autocomplete}
      {min}
      {max}
      {minlength}
      {maxlength}
      {pattern}
      {oninput}
      {onchange}
      {onfocus}
      {onblur}
      {onkeydown}
      {onkeyup}
      {onclick}
      {onpaste}
      {oncut}
    />

    {#if type === 'password'}
      <button
        type="button"
        onclick={togglePassword}
        class="cursor-pointer p-0 border-0 bg-transparent"
        aria-label={showPassword ? 'Hide password' : 'Show password'}
      >
        <img
          src={showPassword ? eyeOpen : eyeClosed}
          alt={showPassword ? 'Hide password' : 'Show password'}
          class="h-[1em]"
        />
      </button>
    {/if}
    {#if rightIcon && type !== 'password'}
      <img src={rightIcon} alt="Right icon" class="h-[1em]" />
    {/if}
  </label>
</fieldset>
