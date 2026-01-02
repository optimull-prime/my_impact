/**
 * API Client for MyImpact backend
 */

// Determine API base URL
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.hostname}`;

/**
 * Fetch metadata (scales, levels, orgs, intensities, styles)
 */
async function fetchMetadata() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/metadata`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch metadata:', error);
        throw error;
    }
}

/**
 * Generate goal prompts based on user inputs
 */
async function generateGoals(payload) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/goals/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `API error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to generate goals:', error);
        throw error;
    }
}

/**
 * Check API health
 */
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        return response.ok;
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}
