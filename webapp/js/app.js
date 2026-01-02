/**
 * MyImpact Web App - Main Application Logic
 */

let cachedMetadata = null;

/**
 * Initialize the application
 */
async function initializeApp() {
    try {
        // Load metadata
        cachedMetadata = await fetchMetadata();

        // Populate dropdowns
        populateScaleDropdown();
        populateOrgDropdown();

        // Setup event listeners
        document.getElementById('scale').addEventListener('change', onScaleChange);
        document.getElementById('prompt-form').addEventListener('submit', onFormSubmit);

        console.log('MyImpact app initialized successfully');
    } catch (error) {
        console.error('Failed to initialize app:', error);
        showError('Failed to load configuration. Please refresh the page.');
    }
}

/**
 * Populate scale dropdown from metadata
 */
function populateScaleDropdown() {
    if (!cachedMetadata) return;

    const scaleSelect = document.getElementById('scale');
    scaleSelect.innerHTML = '<option value="">Select your scale...</option>';

    cachedMetadata.scales.forEach(scale => {
        const option = document.createElement('option');
        option.value = scale;
        option.textContent = scale.charAt(0).toUpperCase() + scale.slice(1);
        scaleSelect.appendChild(option);
    });
}

/**
 * Populate level dropdown based on selected scale
 */
function onScaleChange() {
    const scaleSelect = document.getElementById('scale');
    const selectedScale = scaleSelect.value;

    if (!selectedScale || !cachedMetadata) {
        document.getElementById('level').innerHTML = '<option value="">Select your level...</option>';
        return;
    }

    const levelSelect = document.getElementById('level');
    const levels = cachedMetadata.levels[selectedScale] || [];

    levelSelect.innerHTML = '<option value="">Select your level...</option>';
    levels.forEach(level => {
        const option = document.createElement('option');
        option.value = level;
        option.textContent = level;
        levelSelect.appendChild(option);
    });
}

/**
 * Populate organization dropdown from metadata
 */
function populateOrgDropdown() {
    if (!cachedMetadata) return;

    const orgSelect = document.getElementById('org');
    orgSelect.innerHTML = '<option value="">Select your organization...</option>';

    cachedMetadata.organizations.forEach(org => {
        const option = document.createElement('option');
        option.value = org;
        option.textContent = org.charAt(0).toUpperCase() + org.slice(1);
        orgSelect.appendChild(option);
    });
}

/**
 * Handle form submission
 */
async function onFormSubmit(event) {
    event.preventDefault();

    // Get form values
    const formData = {
        scale: document.getElementById('scale').value,
        level: document.getElementById('level').value,
        growth_intensity: document.querySelector('input[name="growth_intensity"]:checked').value,
        org: document.getElementById('org').value,
        theme: document.getElementById('theme').value || null,
        goal_style: document.querySelector('input[name="goal_style"]:checked').value,
    };

    // Validate required fields
    if (!formData.scale || !formData.level || !formData.org) {
        showError('Please fill in all required fields.');
        return;
    }

    // Show results section and loading state
    document.getElementById('results-section').classList.remove('hidden');
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results-container').classList.add('hidden');
    document.getElementById('error-message').classList.add('hidden');

    // Scroll to results
    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });

    try {
        // Call API
        const response = await generateGoals(formData);

        // Extract prompts
        const systemPrompt = response.prompts[0];
        const userContext = response.prompts[1];

        // Display results
        document.getElementById('system-prompt-content').textContent = systemPrompt;
        document.getElementById('user-context-content').textContent = userContext;

        // Store in window for copy operations
        window.currentPrompts = {
            system: systemPrompt,
            user: userContext,
        };

        // Hide loading, show results
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results-container').classList.remove('hidden');

        // Expand first section by default
        const firstCollapsible = document.querySelector('.collapsible-btn');
        if (firstCollapsible) {
            const nextDiv = firstCollapsible.nextElementSibling;
            nextDiv.classList.remove('hidden');
            firstCollapsible.classList.remove('collapsed');
        }
    } catch (error) {
        console.error('Error generating prompts:', error);
        document.getElementById('loading').classList.add('hidden');
        showError(error.message || 'Failed to generate prompts. Please try again.');
    }
}

/**
 * Toggle collapsible section
 */
function toggleCollapsible(button) {
    const content = button.nextElementSibling;
    const isHidden = content.classList.contains('hidden');

    if (isHidden) {
        content.classList.remove('hidden');
        button.classList.remove('collapsed');
    } else {
        content.classList.add('hidden');
        button.classList.add('collapsed');
    }
}

/**
 * Copy prompt to clipboard
 */
async function copyPrompt(type) {
    if (!window.currentPrompts) return;

    let textToCopy = '';
    let label = '';

    if (type === 'system') {
        textToCopy = window.currentPrompts.system;
        label = 'System Prompt';
    } else if (type === 'user') {
        textToCopy = window.currentPrompts.user;
        label = 'User Context';
    } else if (type === 'both') {
        textToCopy = `[SYSTEM]\n${window.currentPrompts.system}\n\n[USER]\n${window.currentPrompts.user}`;
        label = 'Both Prompts';
    }

    try {
        await navigator.clipboard.writeText(textToCopy);
        showToast(`${label} copied to clipboard!`);
    } catch (error) {
        console.error('Copy failed:', error);
        showError('Failed to copy to clipboard. Try again.');
    }
}

/**
 * Reset form and hide results
 */
function resetForm() {
    document.getElementById('prompt-form').reset();
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('level').innerHTML = '<option value="">Select your level...</option>';
    window.currentPrompts = null;
    document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Start over (same as reset but with results shown)
 */
function startOver() {
    resetForm();
}

/**
 * Show toast notification
 */
function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    toastMessage.textContent = message;
    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

/**
 * Show error message
 */
function showError(message) {
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    errorText.textContent = message;
    errorMessage.classList.remove('hidden');

    // Scroll to error
    errorMessage.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Initialize app on page load
 */
document.addEventListener('DOMContentLoaded', initializeApp);
