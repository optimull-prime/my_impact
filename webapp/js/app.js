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
        document.getElementById('org').addEventListener('change', onOrgChange);
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

    // Allow opting out of organizational focus
    const noneOption = document.createElement('option');
    noneOption.value = 'none';
    noneOption.textContent = 'None (no organizational focus)';
    orgSelect.appendChild(noneOption);

    cachedMetadata.organizations.forEach(org => {
        const option = document.createElement('option');
        option.value = org;
        option.textContent = org.charAt(0).toUpperCase() + org.slice(1);
        orgSelect.appendChild(option);
    });
}

/**
 * Handle organization change - display full org themes
 */
function onOrgChange() {
    const orgSelect = document.getElementById('org');
    const selectedOrg = orgSelect.value;

    const orgThemesContainer = document.getElementById('org-themes-container');
    const orgThemesDisplay = document.getElementById('org-themes-display');

    console.log('Organization changed to:', selectedOrg);

    if (!selectedOrg || selectedOrg === 'none' || !cachedMetadata) {
        orgThemesContainer.classList.add('hidden');
        orgThemesDisplay.value = '';
        return;
    }

    // Fetch and display full org themes content
    console.log('Fetching org themes for:', selectedOrg);
    fetchOrgThemes(selectedOrg).then(content => {
        console.log('Org themes received:', content ? 'YES' : 'NO');
        if (content) {
            orgThemesDisplay.value = content;
            orgThemesContainer.classList.remove('hidden');
        } else {
            orgThemesContainer.classList.add('hidden');
            orgThemesDisplay.value = '';
        }
    }).catch(error => {
        console.error('Error fetching org themes:', error);
        orgThemesContainer.classList.add('hidden');
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
        theme: document.getElementById('theme').value.trim() || null,
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
        
        // Display full prompt preview
        const fullPromptPreview = `[GOAL FRAMEWORK]\n${systemPrompt}\n\n[YOUR CUSTOMIZATION]\n${userContext}`;
        document.getElementById('full-prompt-preview').value = fullPromptPreview;

        // Store in window for copy operations
        window.currentPrompts = {
            system: systemPrompt,
            user: userContext,
        };

        // Hide loading, show results
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results-container').classList.remove('hidden');

        // Keep collapsible sections collapsed by default (user can expand if needed)
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
        label = 'Goal Framework';
    } else if (type === 'user') {
        textToCopy = window.currentPrompts.user;
        label = 'Your Customization';
    } else if (type === 'both') {
        textToCopy = `[GOAL FRAMEWORK]\n${window.currentPrompts.system}\n\n[YOUR CUSTOMIZATION]\n${window.currentPrompts.user}`;
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
    document.getElementById('org-themes-container').classList.add('hidden');
    document.getElementById('org-themes-display').value = '';
    document.getElementById('full-prompt-preview').value = '';
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
