<script lang="ts">
  import Input from '$lib/components/Input.svelte';

  function handleSubmit(event: SubmitEvent) {
    event.preventDefault();

    const formData = new FormData(event.target as HTMLFormElement);
    const name = formData.get('name') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    // TODO: Implement backend authentication
    console.log('Sign up attempt:', { name, email });
    // Future: Send POST request to backend API
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-base-200">
  <div class="card bg-base-100 w-96 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-2xl font-bold mb-2">Get Started</h2>

      <form class="flex flex-col gap-2" onsubmit={handleSubmit}>
        <div>
          <Input
            label="Name"
            id="name"
            name="name"
            placeholder="Full Name"
            type="text"
          />
        </div>

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

        <button type="submit" class="btn btn-primary btn-block mt-4"
          >Sign Up</button
        >

        <div class="divider">Or</div>

        <button type="button" class="btn btn-outline btn-block"
          >Sign up with Google</button
        >

        <div class="text-center text-sm">
          Have an account?
          <a href="/signin" class="link link-hover font-medium">Sign in</a>
        </div>
      </form>
    </div>
  </div>
</div>
