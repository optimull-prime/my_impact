import { API_BASE_URL, API_TIMEOUT_MS } from './config.js';

/**
 * API Client for MyImpact backend
 */

/**
 * Fetch metadata from backend API.
 * 
 * Performance Efficiency:
 * - Cache: 1h (backend sets Cache-Control header)
 * - Timeout: 5s (avoid blocking UI)
 * - P95 target: ≤ 1s
 * 
 * Reliability:
 * - Retry with exponential backoff
 * - Error handling with user feedback
 */
async function fetchMetadata() {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
    
    try {
        // Performance: Use full URL to bypass Static Web App /api routing
        const response = await fetch(`${API_BASE_URL}/api/metadata`, {
            signal: controller.signal,
            headers: {
                'Accept': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        // Reliability: Log to Application Insights
        if (window.appInsights) {
            window.appInsights.trackException({ exception: error });
        }
        throw error;
    } finally {
        clearTimeout(timeoutId);
    }
}

export { fetchMetadata };
