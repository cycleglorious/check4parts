<script lang="ts">
	let { data } = $props();
	let { price_history, error } = data;
</script>

<div class="border-primary-950 overflow-hidden rounded-xl border-2">
  <div class="max-h-[84vh] overflow-y-auto">
    <table class="table min-w-full border-collapse">
      <thead class="bg-primary-950 sticky top-0 z-10">
        <tr class="text-primary-50">
          <th>ID</th>
          <th>Дата створення</th>
          <th>Користувач</th>
          <th>Постачальник</th>
          <th>Chunk ID</th>
          <th>Статус</th>
        </tr>
      </thead>
      <tbody class="!divide-primary-950 !divide-y-2">
        {#each price_history as entry (entry.id)}
          <tr class="divide-primary-950 hover:bg-primary-50 group w-full divide-x-2">
            <td class="p-2">
            {#if entry.status === 'actual' || entry.status === 'deleted'}
              <a
                href={`/home/prices/${entry.id}`}
                class="text-blue-600 hover:text-blue-800 font-medium"
              >
                {entry.id}
              </a>
            {:else}
              {entry.id}
            {/if}
            </td>
            <td class="p-2">
              {new Date(entry.created_at).toLocaleDateString('uk-UA', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </td>
            <td class="p-2">{entry.user.first_name || '—'}</td>
            <td class="p-2">{entry.providers?.name || '—'}</td>
    
            <td class="p-2">{entry.chunk_id || '—'}</td>
            <td class="p-2">
              {#if entry.status === 'uploading'}
                <span class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">
                  Завантаження
                </span>
              {:else if entry.status === 'deleted'}
                <span class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">
                  Видалено
                </span>
              {:else if entry.status === 'actual'}
                <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                  Актуальний
                </span>
              {:else}
                <span class="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">
                  Невідомо
                </span>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

