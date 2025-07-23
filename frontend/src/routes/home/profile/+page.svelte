<script lang="ts">
	let { data } = $props();
	let { user, staff } = $derived(data);
</script>

{#snippet tableRow(name: string, value: string | undefined, badge: boolean = false)}
	<div class="flex items-center gap-4">
		<h4 class="text-surface-200 w-40 font-bold">{name}</h4>
		<p class={badge ? 'badge preset-filled-success-200-800' : 'text-primary-950-50'}>
			{value ? value : 'Не вказано'}
		</p>
	</div>
{/snippet}

<section class="mx-auto h-full w-[95%]">
	<div class="grid grid-cols-[auto_1fr] grid-rows-2 items-center gap-4">
		<div class="row-span-2 flex h-40 w-40 items-center justify-center p-2">
			<img src="/avatar.svg" alt="Аватар" class="h-full w-full object-contain" />
		</div>
		<h2 class="self-end text-2xl font-medium text-gray-800">
			{staff.first_name}
			{staff.last_name}
			{staff.middle_name}
		</h2>
	</div>

	<div
		class="shadow-surface-50 mx-auto mt-6 rounded-xl p-8 shadow-[0px_0px_9px_17px_rgba(0,_0,_0,_0.1)]"
	>
		<header class="mb-4 flex items-center justify-between rounded-xl">
			<h3 class="h5">Контактана інформація</h3>
			<button type="button" class="btn preset-outlined-primary-950-50 !border-2 font-bold"
				>Редагувати</button
			>
		</header>
		<div class="flex flex-col gap-4">
			{@render tableRow('Емейл', user?.email)}
			{@render tableRow('Телефон', staff.phone_number)}
			{@render tableRow('Торгова точка', staff.trading_points?.name)}
			{@render tableRow('Роль', staff.roles.name, true)}
		</div>
	</div>
	{#if user}
		<div
			class="mt-15 shadow-surface-50 mx-auto rounded-xl p-8 shadow-[0px_0px_9px_17px_rgba(0,_0,_0,_0.1)]"
		>
			<header class="mb-4 flex items-center justify-between rounded-xl">
				<h3 class="h5">Безпека</h3>
			</header>
			<div class="flex flex-col gap-4">
				{@render tableRow(
					'Останній вхід',
					user.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleString('uk') : 'Ніколи'
				)}
				{@render tableRow('Дата реєстрації', new Date(user.created_at).toLocaleDateString('uk'))}
				<div class="flex items-center gap-4">
					<h4 class="text-surface-200 w-40 font-bold">Пароль</h4>
					<button type="button" class="btn-sm rounded-md preset-outlined-primary-950-50 !border-2 font-bold"
						>Змінити</button
					>
				</div>
			</div>
		</div>
	{/if}
</section>
