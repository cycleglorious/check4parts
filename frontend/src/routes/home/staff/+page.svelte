<script lang="ts">
	let { data } = $props();
	let { staff, user } = $derived(data);

	let counter = $state<number>(10);
</script>

{#snippet content()}
	<div class="card preset-filled-surface-100-900 h-fit p-4 w-full hover:preset-filled-surface-200-800">
		<h1>Private page for user: {user?.email}</h1>
		<ul class="list-inside list-disc space-y-2">
			{#each staff as person (person.id)}
				<li>{person.name} ( {person.companies.name} )</li>
			{/each}
		</ul>
	</div>
{/snippet}

<section class="flex flex-wrap gap-4">
	{#each Array.from({ length: counter }) as _, index (index)}
		{@render content()}
	{/each}
</section>
