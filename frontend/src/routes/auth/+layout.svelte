<script>
	let { children } = $props();
</script>

<main class="grid h-screen w-screen grid-cols-2 gap-0.5">
	<section class="bg-primary-950"></section>
	<section class=" flex flex-col bg-white align-middle">
		{@render children()}
	</section>
</main>
