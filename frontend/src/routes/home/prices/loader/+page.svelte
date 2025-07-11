<script lang="ts">
  import { enhance } from '$app/forms';
  import { autoMapHeaders } from '$lib/utils/loader/AutoMap.js';
  import { processFile } from '$lib/utils/loader/ProcessFile.js';
  import Worker from '$lib/utils/workers/UploadFiles?worker';
  import { PUBLIC_SUPABASE_PRICES_ANON_KEY, PUBLIC_SUPABASE_PRICES_URL } from '$env/static/public';

  // Props passed from parent (e.g., SvelteKit page load function)
  let { data, form } = $props();

  // Reactive state for selected provider and derived warehouses
  let selected_provider = $state(data.providers?.[0]?.id || '');
  let provider_warehouses = $derived(
    data.warehouses?.filter((wh) => wh.provider_id === selected_provider) || []
  );

  // File processing and UI state
  let fileData: { [k: string]: any }[];
  let count = $state(0); // Total rows in the file

  let files = $state<FileList>();
  let loading = $state(false);
  let previewData = $state<{ [k: string]: any }[]>();
  let headers = $state<string[]>([]);
  let template = $state<any[]>(); // For column mapping
  let progress = $state(0);
  let processing = $state(false); // For worker processing
  let uploadedFiles = $state<string[]>([]);
  let uploadId = $state<string | null>(null);

  let progressLoading = $state(0); // For initial file parsing progress
  let loadingMessage = $state('');

  let hoveredColumnIndex = $state<number | null>(null);

  // --- NEW: Settings state and defaults ---
  type AppSettings = {
    startFrom: number;
    chunkSize: number;
    // Додаємо новий прапорець для стану згортання налаштувань
    settingsCollapsed: boolean;
  };

  const DEFAULT_SETTINGS: AppSettings = {
    startFrom: 2, // Default to start from the second row
    chunkSize: 7000, // Default chunk size
    settingsCollapsed: false // Default to not collapsed
  };

  let settings = $state<AppSettings>(DEFAULT_SETTINGS);

  // Load settings from localStorage on component initialization
  $effect(() => {
    try {
      const storedSettings = localStorage.getItem('appSettings');
      if (storedSettings) {
        // Merge with defaults to handle new properties gracefully
        settings = { ...DEFAULT_SETTINGS, ...JSON.parse(storedSettings) };
      }
    } catch (e) {
      console.error('Failed to load settings from localStorage:', e);
      settings = DEFAULT_SETTINGS; // Fallback to defaults
    }
  });

  // Save settings to localStorage whenever they change
  $effect(() => {
    try {
      localStorage.setItem('appSettings', JSON.stringify(settings));
    } catch (e) {
      console.error('Failed to save settings to localStorage:', e);
    }
  });
  // --- END NEW: Settings state and defaults ---

  let missingRequired = $derived(
    template?.filter((t) => t.required && !t.header).map((t) => t.name) || []
  );

  async function handleProcessing() {
    progress = 0;
    processing = true;

    const worker = new Worker();
    const cleanTemplate = JSON.parse(JSON.stringify(template));

    worker.postMessage({
      fileData,
      template: cleanTemplate,
      chunkSize: settings.chunkSize, // Use value from settings
      session: data.session,
      supabaseUrl: PUBLIC_SUPABASE_PRICES_URL,
      supabaseAnonKey: PUBLIC_SUPABASE_PRICES_ANON_KEY
    });

    worker.onmessage = (e) => {
      const { type, value, uploadedFiles: files, error, uploadId: uuid } = e.data;

      if (type === 'progress') {
        progress = value;
      } else if (type === 'mapped') {
        console.log('Data Mapped');
      } else if (type === 'done') {
        processing = false;
        uploadedFiles = files;
        uploadId = uuid || null;
        worker.terminate();
      } else if (type === 'error') {
        console.error(error);
        alert('❌ Помилка при завантаженні: ' + error);
        processing = false;
        worker.terminate();
      }
    };
  }

  function handleMouseEnter(index: number) {
    hoveredColumnIndex = index;
  }

  function handleMouseLeave() {
    hoveredColumnIndex = null;
  }

  // Effect to reset processing state if form submission occurs (e.g., after final import)
  $effect(() => {
    if (form) {
      processing = false;
    }
  });

  async function handleFileSubmit(e: Event) {
    e.preventDefault();
    loading = true;
    template = []; // Reset template on new file upload attempt
    console.log('Starting file processing...');
    await processFile(files!, settings.startFrom, 5, 0, { // Use settings.startFrom
      onPreview: ({ previewData: pd }) => {
        previewData = pd;
        headers = Array.from(Object.values(pd[0]));
        template = autoMapHeaders(headers, provider_warehouses);
      },
      onFull: ({ fileData: fd }) => {
        fileData = fd;
        loading = false;
        count = fd.length;
      },
      onProgress: ({ message, percentage }) => {
        loadingMessage = message;
        progressLoading = percentage;
      }
    });
  }

  // Function to toggle settings collapse state
  function toggleSettingsCollapse() {
    settings.settingsCollapsed = !settings.settingsCollapsed;
  }
</script>

<section class="card settings-card" aria-label="Налаштування імпорту">
  <h3 class="card-title">
    <button class="toggle-button" onclick={toggleSettingsCollapse} aria-expanded={!settings.settingsCollapsed}>
      Налаштування
    </button>
  </h3>
  {#if !settings.settingsCollapsed}
    <div class="form-grid">
      <div class="form-group">
        <label for="startFromInput">Почати обробку з рядка</label>
        <input
          id="startFromInput"
          type="number"
          min="1"
          bind:value={settings.startFrom}
          placeholder="Наприклад, 2"
          required
          disabled={loading || !!template}
        />
        <p class="form-hint">Вкажіть номер рядка, з якого почнеться обробка даних у файлі.</p>
      </div>

      <div class="form-group">
        <label for="chunkSizeInput">Розмір чанка</label>
        <input
          id="chunkSizeInput"
          type="number"
          min="1"
          bind:value={settings.chunkSize}
          required
          disabled={loading || processing}
        />
        <p class="form-hint">
          Вкажіть максимальну кількість рядків для обробки в одному чанку. Більші чанки швидші, але
          вимагають більше пам'яті.
        </p>
      </div>
    </div>
  {/if}
</section>


<form
  onsubmit={handleFileSubmit}
  aria-label="Завантаження файлу та вибір провайдера"
  class="card"
>
  <div class="form-group">
    <label for="providerSelect">Оберіть провайдера</label>
    <select id="providerSelect" bind:value={selected_provider} required disabled={!!template}>
      {#each data.providers || [] as provider}
        <option value={provider.id}>{provider.name}</option>
      {/each}
    </select>
  </div>

  <div class="form-group">
    <label for="fileInput">Оберіть файл для завантаження</label>
    <input
      id="fileInput"
      type="file"
      accept=".xlsx,.xls,.csv,.txt"
      bind:files
      required
      disabled={!!template}
    />
  </div>

  <div class="form-group button-group">
    <button class="btn btn-success" type="submit" disabled={loading} aria-busy={loading}>
      {#if loading}
        Обробка...
      {:else}
        Завантажити файл
      {/if}
    </button>
  </div>
</form>

{#if progressLoading > 0 && loading}
  <div
    class="progress-container"
    role="progressbar"
    aria-valuemin="0"
    aria-valuemax="100"
    aria-valuenow={progressLoading}
    aria-label="Індикатор завантаження файлу"
  >
    <div class="progress-bar" style="width: {progressLoading}%"></div>
    <p class="progress-text">{progressLoading}% {loadingMessage}</p>
  </div>
{/if}

{#if previewData && template && previewData.length > 0}
  <section class="card" aria-label="Попередній перегляд даних">
    <h3 class="card-title">Попередній перегляд</h3>
    {#if count > 0}
      <p class="form-hint">
        Показано {previewData.length} з {count} рядків (Починаючи з {settings.startFrom})
      </p>
    {:else}
      <p class="form-hint">Немає даних для попереднього перегляду</p>
    {/if}

    <div class="table-container">
      <table>
        <thead>
          <tr>
            {#each headers as h, i (i)}
              <th
                scope="col"
                class:hovered={hoveredColumnIndex === i}
                onmouseenter={() => handleMouseEnter(i)}
                onmouseleave={handleMouseLeave}
                tabindex="0"
                aria-colindex={i + 1}
              >
                Колонка {i + 1} ({h})
              </th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each previewData as row, rowIndex (rowIndex)}
            <tr>
              {#each headers as h, colIndex (colIndex)}
                <td class:hovered={hoveredColumnIndex === colIndex} aria-colindex={colIndex + 1}>
                  {Array.from(Object.values(row))[colIndex] || ''}
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>

  <section class="card mapping-section" aria-label="Відповідність колонок">
    <h3 class="card-title">Відповідність колонок</h3>

    {#if missingRequired.length > 0}
      <p class="alert alert-error" role="alert" aria-live="assertive">
        Не заповнено: {missingRequired.join(', ')}
      </p>
    {/if}

    <div class="mapping-grid">
      {#each template as item (item.value)}
        <div class="mapping-row">
          <label for={item.value}>{item.name}:</label>
          <select
            id={item.value}
            bind:value={item.header}
            aria-label={`Вибрати колонку для ${item.name}`}
          >
            <option value="">—</option>
            {#each headers as h, i}
              <option value={i}>
                {#if h}
                  Колонка {h} ({i + 1})
                {:else}
                  Колонка {i + 1}
                {/if}
              </option>
            {/each}
          </select>
        </div>
      {/each}
    </div>
    <div class="action-button-container">
      <button
        onclick={() => handleProcessing()}
        class="btn btn-primary"
        disabled={loading || processing || missingRequired.length > 0}
        aria-busy={processing}
        aria-label="Почати обробку і завантаження"
      >
        {#if processing}
          Обробка даних...
        {:else}
          Почати обробку і завантаження
        {/if}
      </button>
    </div>
  </section>
{/if}

{#if processing}
  <div
    class="progress-container"
    role="progressbar"
    aria-valuemin="0"
    aria-valuemax="100"
    aria-valuenow={progress}
    aria-label="Індикатор завантаження"
  >
    <div class="progress-bar" style="width: {progress}%"></div>
    <p class="progress-text">{progress}% Завантаження</p>
  </div>
{/if}

{#if uploadedFiles.length > 0}
  <form
    method="POST"
    action="?/processChunks"
    use:enhance
    aria-label="Завершення імпорту"
    class="card upload-form"
    onsubmit={() => {
      processing = true;
    }}
  >
    <h3 class="card-title">Завершення імпорту</h3>
    <p class="upload-id-text">ID: {uploadId}</p>

    <input type="hidden" name="processedData" value={uploadedFiles.join(',')} />
    <input type="hidden" name="provider_id" value={selected_provider} />

    <div class="action-button-container">
      <button
        type="submit"
        class="btn btn-success"
        aria-label="Завершити імпорт"
        aria-busy={processing}
        disabled={processing || uploadedFiles.length === 0}
      >
        {#if processing}
          Завантаження...
        {:else}
          <span class="icon">📤</span> Завершити імпорт ({uploadedFiles.length} частин)
        {/if}
      </button>
    </div>
  </form>
{/if}

{#if form}
  <section
    class="card result-card"
    class:success={form.success}
    class:error={!form.success}
    aria-live="polite"
    aria-atomic="true"
  >
    {#if form.success && form.stats}
      <h3 class="card-title result-title success-text">✅ Успішний імпорт</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <dt class="stat-label">Оброблено чанків:</dt>
          <dd class="stat-value">{form.stats.processed}</dd>
        </div>
        <div class="stat-item">
          <dt class="stat-label">Успішно імпортовано:</dt>
          <dd class="stat-value">
            {form.stats.succeeded} / {form.stats.processed}
          </dd>
        </div>
        <div class="stat-item">
          <dt class="stat-label">Нових записів:</dt>
          <dd class="stat-value">{form.stats.remaining}</dd>
        </div>
      </div>
    {:else}
      <h3 class="card-title result-title error-text">❌ Помилка імпорту</h3>
      <p class="error-message">{form.message || 'Невідома помилка'}</p>
    {/if}

    {#if form.missing && form.missing.brands?.length > 0}
      <div class="missing-section">
        <h4 class="section-subtitle">
          Відсутні бренди ({form.missing.brands.length})
        </h4>
      </div>
    {/if}

    {#if form.missing && form.missing.articles?.length > 0}
      <div class="missing-section">
        <h4 class="section-subtitle">
          Відсутні артикули ({form.missing.articles.length})
        </h4>
      </div>
    {/if}

    {#if form.missing && form.missing.articlesFile}
      <div class="download-section">
        <a
          href={`loaderv2/reports?file=${form.missing.articlesFile}`}
          target="_blank"
          download
          class="btn btn-download"
          aria-label="Завантажити файл відсутніх артикулів у форматі CSV"
        >
          📥 Завантажити файл відсутніх артикулів (.csv)
        </a>
        <p class="form-hint">Файл доступний за посиланням на Supabase Storage.</p>
      </div>
    {/if}

    {#if form.errors && form.errors?.length > 0}
      <div class="error-list-section" role="alert" aria-live="assertive">
        <h4 class="section-subtitle error-text">
          Помилки обробки чанків ({form.errors.length})
        </h4>
        <ul class="error-list">
          {#each form.errors as error}
            <li><strong>{error.chunk}</strong>: {error.error}</li>
          {/each}
        </ul>
      </div>
    {/if}
  </section>
{/if}

<style>
  /* Base Styles & Variables */

  :root {
    /* Colors */
    --primary-blue: #3b82f6;
    --primary-blue-dark: #2563eb;
    --primary-green: #10b981;
    --primary-green-dark: #059669;
    --red-error: #ef4444;
    --red-error-light: #fef2f2;
    --text-color-default: #334155;
    --text-color-secondary: #475569;
    --text-color-muted: #64748b;
    --bg-color-light: #f8fafc;
    --bg-color-white: #ffffff;
    --bg-color-hover: #dbeafe;
    --bg-color-table-stripe: #f8fafc;
    --border-color-default: #e2e8f0;
    --border-color-input: #cbd5e1;
    --focus-ring-color: rgba(59, 130, 246, 0.25);
    --shadow-default: 0 4px 16px rgba(0, 0, 0, 0.05);
    --shadow-button: 0 2px 4px rgba(59, 130, 246, 0.2);
    --shadow-button-hover: 0 4px 6px rgba(59, 130, 246, 0.25);
    --shadow-green-button: 0 2px 4px rgba(16, 185, 129, 0.2);
    --shadow-green-button-hover: 0 4px 6px rgba(16, 185, 129, 0.25);

    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 0.85rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-xxl: 2.5rem;

    /* Border Radius */
    --radius-sm: 8px;
    --radius-md: 12px;

    /* Font Sizes */
    --font-size-sm: 0.85rem;
    --font-size-default: 1rem;
    --font-size-lg: 1.25rem;
    --font-size-xl: 1.5rem;
  }

  /* Typography */
  h3,
  h4 {
    color: #1e293b;
    font-weight: 600;
  }

  h3 {
    font-size: var(--font-size-xl);
    margin-top: 0;
    margin-bottom: var(--spacing-lg);
  }

  h4 {
    font-size: var(--font-size-lg);
    margin-top: 0;
    margin-bottom: var(--spacing-md);
  }

  .card-title {
    margin-bottom: var(--spacing-lg);
  }

  .form-hint {
    font-size: var(--font-size-sm);
    color: var(--text-color-muted);
    margin-top: var(--spacing-xs);
  }

  /* Layout & Components */
  .card {
    background-color: var(--bg-color-white);
    padding: var(--spacing-xl);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-default);
    margin-bottom: var(--spacing-xl);
    border: 1px solid var(--border-color-default);
  }

  .upload-form {
    gap: var(--spacing-lg);
    justify-items: center; /* Center items in the form */
  }

  /* Main file upload form layout */
  form {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    align-items: start; /* Aligns items to the top */
    gap: var(--spacing-lg);
  }

  /* Settings form layout (new) */
  .settings-card .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-lg);
    /* Transition for smooth collapse/expand */
    overflow: hidden;
    transition: all 0.3s ease-out;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .button-group {
    align-self: center; /* Center the button group */
    margin-top: var(--spacing-xs);
    height: 100%;
  }

  .button-group button {
    width: 100%; /* Make buttons full width */
    height: 100%;
  }

  label {
    font-weight: 500;
    color: var(--text-color-secondary);
    font-size: 0.95rem;
  }

  select,
  input[type='text'],
  input[type='number'],
  input[type='file'] {
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--border-color-input);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-default);
    color: var(--text-color-default);
    background-color: var(--bg-color-light);
    transition: all 0.2s ease;
  }

  select:focus,
  input:focus {
    border-color: var(--primary-blue);
    outline: none;
    box-shadow: 0 0 0 3px var(--focus-ring-color);
  }

  /* Buttons */
  .btn {
    padding: var(--spacing-sm) 1.75rem;
    border: none;
    border-radius: var(--radius-sm);
    color: white;
    font-size: var(--font-size-default);
    font-weight: 500;
    cursor: pointer;
    transition:
      background-color 0.2s ease,
      transform 0.1s ease,
      box-shadow 0.2s ease;
    height: fit-content;
    display: inline-flex; /* Use inline-flex for better alignment with text/icons */
    align-items: center;
    justify-content: center;
    gap: var(--spacing-xs);
    text-decoration: none; /* For download links */
  }

  .btn:hover:not(:disabled) {
    transform: translateY(-1px);
  }

  .btn:disabled {
    background-color: var(--border-color-input);
    cursor: not-allowed;
    box-shadow: none;
  }

  .btn-default {
    background-color: var(--primary-blue);
    box-shadow: var(--shadow-button);
  }

  .btn-default:hover:not(:disabled) {
    background-color: var(--primary-blue-dark);
    box-shadow: var(--shadow-button-hover);
  }

  .btn-primary {
    background-color: var(--primary-green);
    box-shadow: var(--shadow-green-button);
  }

  .btn-primary:hover:not(:disabled) {
    background-color: var(--primary-green-dark);
    box-shadow: var(--shadow-green-button-hover);
  }

  .btn-success {
    background-color: var(--primary-green);
    box-shadow: var(--shadow-green-button);
  }

  .btn-success:hover:not(:disabled) {
    background-color: var(--primary-green-dark);
    box-shadow: var(--shadow-green-button-hover);
  }

  .btn-download {
    background-color: var(--primary-green);
    box-shadow: var(--shadow-green-button);
  }

  .btn-download:hover {
    background-color: var(--primary-green-dark);
    box-shadow: var(--shadow-green-button-hover);
  }

  .action-button-container {
    margin-top: var(--spacing-md);
    margin-bottom: var(--spacing-xs);
  }

  /* Table Styles */
  .table-container {
    overflow-x: auto;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-color-default);
    margin-top: var(--spacing-md);
  }

  table {
    width: 100%;
    border-collapse: separate; /* For rounded corners on border-radius parent */
    border-spacing: 0;
    min-width: 600px;
    font-size: 0.9rem;
    color: var(--text-color-default);
  }

  th {
    background-color: #f1f5f9;
    padding: var(--spacing-md);
    text-align: left;
    font-weight: 600;
    color: var(--text-color-secondary);
    border-bottom: 1px solid var(--border-color-default);
    /* For top-left/right rounded corners */
    &:first-child {
      border-top-left-radius: var(--radius-sm);
    }
    &:last-child {
      border-top-right-radius: var(--radius-sm);
    }
  }

  td {
    padding: 0.8rem var(--spacing-md);
    border-bottom: 1px solid var(--border-color-default);
  }

  tr:last-child td {
    border-bottom: none;
  }

  tr:nth-child(even) {
    background-color: var(--bg-color-table-stripe);
  }

  th.hovered,
  td.hovered {
    background-color: var(--bg-color-hover);
  }

  /* Mapping Section */
  .mapping-section {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .mapping-grid {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .mapping-row {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  /* Alerts & Messages */
  .alert {
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-sm);
    font-weight: 500;
  }

  .alert-error {
    color: var(--red-error);
    background-color: var(--red-error-light);
  }

  /* Progress Bar */
  .progress-container {
    background-color: var(--border-color-default);
    border-radius: var(--radius-sm);
    overflow: hidden;
    margin-bottom: var(--spacing-lg);
    height: 28px;
    position: relative;
  }

  .progress-bar {
    background: linear-gradient(90deg, var(--primary-blue), #60a5fa);
    height: 100%;
    transition: width 0.4s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .progress-text {
    position: absolute;
    width: 100%;
    text-align: center;
    font-weight: 500;
    color: var(--text-color-default);
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
  }

  /* Result Card */
  .result-card {
    padding: var(--spacing-lg) var(--spacing-xl); /* Adjusted padding */
    margin-top: var(--spacing-xl);
    border-left-width: 4px;
    border-left-style: solid;
  }

  .result-card.success {
    background-color: #f0fdf4;
    border-color: var(--primary-green);
  }

  .result-card.error {
    background-color: var(--red-error-light);
    border-color: var(--red-error);
  }

  .result-title {
    margin-bottom: var(--spacing-md);
  }

  .success-text {
    color: var(--primary-green-dark);
  }

  .error-text {
    color: var(--red-error);
  }

  .error-message {
    color: var(--red-error);
    font-weight: 500;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
    margin: var(--spacing-lg) 0;
  }

  .stat-item {
    background-color: var(--bg-color-table-stripe);
    padding: var(--spacing-md);
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-color-default);
  }

  .stat-label {
    font-weight: 500;
    color: var(--text-color-muted);
    font-size: 0.95rem;
  }

  .stat-value {
    font-weight: 600;
    color: #1e293b;
    font-size: var(--font-size-lg);
    margin: var(--spacing-xs) 0 0 0;
  }

  .missing-section,
  .error-list-section {
    background-color: #fff1f2; /* Lighter red for missing/errors */
    padding: var(--spacing-lg);
    border-radius: var(--radius-sm);
    margin-top: var(--spacing-lg);
    color: #881337; /* Darker red text for missing/errors */
    border: 1px solid #fecaca;
  }

  .section-subtitle {
    font-weight: 600;
    margin-bottom: var(--spacing-xs);
  }

  .download-section {
    margin-top: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--border-color-default);
  }

  .error-list {
    list-style: disc;
    margin-left: var(--spacing-lg);
    padding-left: 0;
  }

  .error-list li {
    margin-bottom: var(--spacing-xs);
  }

  /* Styles for toggle button */
  .toggle-button {
    background: none;
    border: none;
    padding: 0;
    font-size: inherit;
    font-weight: inherit;
    color: inherit;
    cursor: pointer;
    display: flex;
    align-items: center;
    /* gap: 0.5rem; */
  }

  .toggle-icon {
    font-size: 0.8em;
    transition: transform 0.3s ease;
  }

  /* Responsive Adjustments */
  @media (max-width: 768px) {
    :global(body) {
      padding: 1rem;
    }

    form {
      grid-template-columns: 1fr;
    }

    .table-container {
      -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
    }

    .mapping-grid {
      grid-template-columns: 1fr;
    }

    .stats-grid {
      grid-template-columns: 1fr;
    }

    .btn {
      width: 100%;
      padding: 1rem;
    }

    .card,
    .form {
      padding: var(--spacing-lg);
    }
  }

  @media (max-width: 480px) {
    :global(body) {
      padding: 0.75rem;
    }

    h3 {
      font-size: 1.3rem;
    }

    h4 {
      font-size: 1.1rem;
    }

    .card {
      padding: var(--spacing-md);
    }
  }
</style>