<script lang="ts">
	import { slide } from 'svelte/transition';
	import CartButton from './(components)/CartButton.svelte';

	interface Props {
		part: {
			id: string;
			name: string;
			code: string;
			description: string; // can be big string
			image: string;
			brand: {
				id?: string;
				name: string; // name of brand
			};
			details: {
				id?: string;
				value: string; // value to display
				title: string; // title to display
				name: string; // name in database column
			}[];
		};
		rests: {
			id?: string;
			provider: {
				id?: string;
				name: string; // name of provider
			};
			quantity: number; // quantity of part
			delivery_time: string; // delivery time of part
			price: number; // price of part
		}[];
	}

	let { part, rests }: Props = $props();

	let collapsedContent = $state(false);
	let showDetails = $state(false);
</script>

<div class="card border-primary-950 flex flex-col overflow-hidden rounded-xl border-1">
	<div
		id="header"
		class="bg-primary-950 text-primary-50 flex items-center justify-between gap-2 px-4 py-2"
	>
		<h3 class="h5">{part.name}</h3>
		<button
			type="button"
			class="btn preset-filled-primary-950-50"
			onclick={() => (collapsedContent = !collapsedContent)}
			aria-expanded={collapsedContent}
			aria-controls="content"
		>
			<img
				src="/arrow.svg"
				alt="collapse"
				class="size-6 transition-all"
				class:rotate-180={collapsedContent}
			/>
		</button>
	</div>
	{#if !collapsedContent}
		<div id="content" transition:slide={{ duration: 200 }} class="rounded-b-xl">
			<div class="flex flex-row gap-4 p-4 justify-between">
				<div class="flex gap-4 p-4">
					<div>
						<img src={part.image} alt={part.name} class="object-cover" />
					</div>
					<div>
						<h3 class="h5">{part.name}</h3>
						<p>{part.description}</p>
						<p>Код: {part.code}</p>
						<p>Виробник: {part.brand.name}</p>
					</div>
				</div>
				<div id="rests" class="overflow-auto">
					<table>
						<thead>
							<tr>
								<th class="px-5 text-center font-normal tracking-wider text-gray-500"
									>Постачальник</th
								>
								<th class="px-5 text-center font-normal tracking-wider text-gray-500">Кількість</th>
								<th class="px-5 text-center font-normal tracking-wider text-gray-500"
									>Час доставки</th
								>
								<th class="px-5 text-center font-normal tracking-wider text-gray-500">Ціна (грн)</th
								>
							</tr>
						</thead>
						<tbody class="bg-white">
							{#each rests as rest}
								<tr class="hover:bg-gray-50">
									<td class="rounded-l-2xl p-2 text-center">{rest.provider.name}</td>
									<td class="p-2 text-center">{rest.quantity}</td>
									<td class="p-2 text-center">{rest.delivery_time}</td>
									<td class="p-2 text-center">{rest.price} грн</td>
									<td class="rounded-r-2xl p-2 text-center"><CartButton {part} /></td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
			<div id="footer" class="p-4 flex flex-row justify-between">
				<div id="details">
					<button
						type="button"
						class="uppercase underline p-0 flex items-center gap-2"
						onclick={() => (showDetails = !showDetails)}
					>
						{showDetails ? 'Сховати деталі' : 'Показати деталі'}
            <img
              src="/details-arrow.svg"
              alt="collapse"
              class="size-4 transition-all"
              class:rotate-180={showDetails}
            />
					</button>
					{#if showDetails}
						<div class="flex flex-col" transition:slide={{ duration: 200 }}>
							{#each part.details as detail}
								<div class="grid grid-cols-[auto_1fr] gap-3">
									<p class="font-bold">{detail.title}:</p>
									<p>{detail.value}</p>
								</div>
							{/each}
						</div>
					{/if}
				</div>
        <div>
          <p class="uppercase underline"> 
            Замінники
          </p>
        </div>
			</div>
		</div>
	{/if}
</div>
