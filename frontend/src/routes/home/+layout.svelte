<script lang="ts">
	import { Navigation } from '@skeletonlabs/skeleton-svelte';

	let { data, children } = $props();
	let { supabase } = $derived(data);

	const logout = async () => {
		const { error } = await supabase.auth.signOut();
		if (error) {
			console.error(error);
		}
		window.location.href = '/auth';
	};

	let isExpansed = $state(false);
	let page = $state<'home' | 'staff'>();

	const toggleExpanded = () => {
		isExpansed = !isExpansed;
	};
</script>

<header class="card border-surface-100-900 grid h-screen w-full grid-cols-[auto_1fr] border-[1px]">
	<Navigation.Rail value={page} expanded={isExpansed}>
		{#snippet header()}
			<Navigation.Tile onclick={toggleExpanded}>Menu</Navigation.Tile>
		{/snippet}
		{#snippet tiles()}
			<Navigation.Tile labelExpanded="Home" href="/home" id="home" onclick={() => (page = 'home')}
				>Home</Navigation.Tile
			>
			<Navigation.Tile
				labelExpanded="Staff"
				href="/home/staff"
				id="staff"
				onclick={() => (page = 'staff')}>Staff</Navigation.Tile
			>
		{/snippet}
		{#snippet footer()}
			<Navigation.Tile onclick={logout}>Logout</Navigation.Tile>
		{/snippet}
	</Navigation.Rail>
	<div>
		{@render children()}
	</div>
</header>
