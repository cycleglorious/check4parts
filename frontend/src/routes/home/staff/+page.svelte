<script lang="ts">
	let { data } = $props();
	let { staff, user } = $derived(data);
</script>

<section class=" container p-4">
	<div
		class="card preset-filled-surface-100-900 border-surface-200-800 w-full max-w-md border-[1px] p-4 text-center"
	>
		<h1>Private page for user: {user?.email}</h1>
		<ul class="list-inside list-disc space-y-2">
			{#each staff as person (person.id)}
				<li>{person.name} ( {person.companies.name} )</li>
			{/each}
		</ul>
	</div>
</section>
