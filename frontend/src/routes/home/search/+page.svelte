<script lang="ts">
	import SearchResultCard from '$lib/components/cards/search/SearchResultCard.svelte';
	import type { PageData } from './$types'; // Типи для даних, що повертаються з load

	// Отримуємо дані з load функції +page.server.ts
	// data.searchQuery буде доступний одразу
	// data.parts буде Promise
	const { data } = $props<{ data: PageData }>(); // Типізація пропсів Svelte 5

	const searchQuery = $derived(data.searchQuery); // Реактивне отримання searchQuery
</script>

<div class="container mx-auto p-4">
	<h1 class="mb-6 text-2xl font-bold">
		{#if searchQuery}
			Результати пошуку для: "{searchQuery}"
		{:else}
			Введіть запит для пошуку
		{/if}
	</h1>

	{#await data.parts}
		<div class="text-center text-gray-500">
			<p class="mb-2">Завантаження результатів пошуку...</p>
			<svg
				class="mx-auto h-8 w-8 animate-spin text-blue-500"
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
			>
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
				></circle>
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				></path>
			</svg>
		</div>
	{:then parts}
		{#if parts}
			{#if parts.length === 0 && searchQuery}
				<p class="text-center text-lg text-gray-600">
					За вашим запитом "{searchQuery}" нічого не знайдено.
				</p>
			{:else if parts.length === 0 && !searchQuery}
				<p class="text-center text-lg text-gray-600">
					Введіть щось у поле пошуку, щоб знайти запчастини.
				</p>
			{:else}
				<div class="grid gap-6">
					{#each parts as part (part.code)}
						<SearchResultCard {part} rests={part.rests} />
					{/each}
				</div>
			{/if}
		{/if}
	{:catch error}
		<p class="text-center text-lg text-red-500">
			Помилка при завантаженні результатів: {error.message}
		</p>
	{/await}
</div>
