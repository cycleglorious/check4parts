<script lang="ts">
	import { Tabs } from '@skeletonlabs/skeleton-svelte';
	import RestsTab from './(tabs)/RestsTab.svelte';
	import DetailsTab from './(tabs)/DetailsTab.svelte';
	import CrossTab from './(tabs)/CrossTab.svelte';
	import AdditionalTab from './(tabs)/AdditionalTab.svelte';

	let { data } = $props();
	let { part, rests, crosses, additional } = $derived(data);

	let group = $state('rests');
</script>

{#snippet tableRow(name: string, value: string)}
	<tr class="odd:bg-white even:bg-gray-50 odd:dark:bg-gray-900">
		<td class="text-primary-950-50 p-4 font-bold">{name}</td>
		<td class="p-4 font-light">{value}</td>
	</tr>
{/snippet}

<section id="content">
	<div class="grid grid-cols-[1fr_4fr] gap-10">
		<div>
			<img src={part.image} alt={part.name} class="w-full object-cover object-center" />
		</div>
		<div class="flex flex-col gap-8">
			<div>
				<h3 class="h5">{part.code}</h3>
				<p class="text-primary-950-50 text-sm">{part.name}</p>
			</div>
			<table class="w-full text-left text-sm text-gray-500 rtl:text-right dark:text-gray-400">
				<tbody>
					{@render tableRow('Виробник', part.brand.name)}
					{@render tableRow('Код', part.code)}
					{@render tableRow('Опис', part.description)}
				</tbody>
			</table>
		</div>
	</div>
</section>

<section id="tabs" class="overflow-hidden">
	<Tabs
		value={group}
		onValueChange={(e) => {
			group = e.value;
		}}
	>
		{#snippet list()}
			<Tabs.Control stateActive="font-normal !border-b-3 !border-primary-950" value="rests"
				>Порівняння цін</Tabs.Control
			>
			<Tabs.Control stateActive="font-normal !border-b-3 !border-primary-950" value="details"
				>Деталі</Tabs.Control
			>
			<Tabs.Control stateActive="font-normal !border-b-3 !border-primary-950" value="cross"
				>Замінники</Tabs.Control
			>
			<Tabs.Control stateActive="font-normal !border-b-3 !border-primary-950" value="additional"
				>Супутні товари</Tabs.Control
			>
		{/snippet}
		{#snippet content()}
			<Tabs.Panel value="rests">
				<div class="max-w-6xl">
					<RestsTab {rests} />
				</div>
			</Tabs.Panel>
			<Tabs.Panel value="details">
				<div class="max-w-6xl">
					<DetailsTab details={part.details} />
				</div>
			</Tabs.Panel>
			<Tabs.Panel value="cross">
				<CrossTab {crosses} />
			</Tabs.Panel>
			<Tabs.Panel value="additional">
				<div class="max-w-6xl">
					<AdditionalTab {additional} />
				</div>
			</Tabs.Panel>
		{/snippet}
	</Tabs>
</section>
