<script lang="ts">
	import { goto } from '$app/navigation';

	$effect(() => {
		goto('/home/settings/users');
	});
</script>
