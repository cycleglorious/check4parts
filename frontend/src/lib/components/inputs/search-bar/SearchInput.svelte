<script lang="ts">
	let {
		name,
		placeholder,
		required = false,
		value = $bindable(),
		gotoOnSearch
	}: {
		name: string;
		placeholder: string;
		required?: boolean;
		value?: string;
		gotoOnSearch?: (value: string) => void;
	} = $props();
</script>

<label class="label relative block w-full">
	<input
		class="input focus:outline-primary-500 h-10 rounded-3xl bg-white px-4 pr-14 shadow-none outline-2 placeholder:text-gray-400"
		{name}
		type="text"
		{placeholder}
		{required}
		bind:value
		onkeydown={(e) => {
			if (e.key === 'Enter') {
				e.preventDefault();
				gotoOnSearch?.(value!);
			}
		}}
	/>
	<button
		type="button"
		class="absolute top-1 right-4"
		onclick={() => {
			gotoOnSearch?.(value!);
		}}
	>
		<img src="/search-icon.svg" alt="search" class="size-6" />
	</button>
</label>
