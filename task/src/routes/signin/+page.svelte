<script lang="ts">
  import Input from '$lib/components/Input.svelte';

  function handleSubmit(event: SubmitEvent) {
    event.preventDefault();

    const formData = new FormData(event.target as HTMLFormElement);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const remember = formData.get('remember') === 'on';

    // TODO: Implement backend authentication
    console.log('Sign in attempt:', { email, remember });
    // Future: Send POST request to backend API
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-base-200">
  <div class="card bg-base-100 w-96 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-2xl font-bold mb-2">Welcome Back</h2>

      <form class="flex flex-col gap-2" onsubmit={handleSubmit}>
        <div>
          <Input
            label="Email"
            id="email"
            name="email"
            placeholder="Enter your email"
            type="email"
          />
        </div>

        <div>
          <Input
            label="Password"
            id="password"
            name="password"
            placeholder="Password"
            type="password"
          />
        </div>

        <div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              class="checkbox checkbox-sm"
              id="remember"
              name="remember"
            />
            <span class="label-text">Remember me</span>
          </label>
        </div>

        <button type="submit" class="btn btn-primary btn-block mt-4"
          >Sign In</button
        >

        <div class="divider">Or</div>

        <button type="button" class="btn btn-outline btn-block"
          >Sign in with Google</button
        >

        <div class="text-center text-sm">
          Don't have an account?
          <a href="/signup" class="link link-hover font-medium">Sign up</a>
        </div>
      </form>
    </div>
  </div>
</div>
