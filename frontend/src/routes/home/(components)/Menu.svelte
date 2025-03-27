<script lang="ts">
	let { page }: { page: string } = $props();
	import { slide } from 'svelte/transition';
</script>

{#snippet menuItem(pageValue: string, pageTitle: string)}
	<a
		class:font-bold={page === pageValue}
		class:hover:font-medium={page !== pageValue}
		href="/home/{pageValue}"
		class="flex items-center gap-2 text-xl"
	>
		<img
			src={page === pageValue ? `/settings-icon-selected.svg` : `/settings-icon.svg`}
			alt={pageValue}
			class=" size-6"
		/>
		{pageTitle}
	</a>
{/snippet}

{#snippet subMenu(pageValue: string, subPages: { href: string; title: string }[])}
	{#if page === pageValue}
		<ul class="pl-9" transition:slide={{ duration: 200 }}>
			{#each subPages as subPage (subPage.href)}
				<li>
					<a href={subPage.href} class="anchor">{subPage.title}</a>
				</li>
			{/each}
		</ul>
	{/if}
{/snippet}

<div class="flex flex-col gap-2">
	<ul>
		<li>
			{@render menuItem('staff', 'Співробітники')}
			{@render subMenu('staff', [
				{ href: 'staff/0', title: 'Співробітники' },
				{ href: 'staff/1', title: 'Додати співробітника' }
			])}
		</li>
		<li>
			{@render menuItem('settings', 'Налаштування')}
			{@render subMenu('settings', [
				{ href: 'settings/0', title: 'Налаштування' },
				{ href: 'settings/1', title: 'Додати налаштування' }
			])}
		</li>
	</ul>
</div>
