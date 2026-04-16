/**
 * cass Archive Service Worker Registration
 *
 * Handles service worker registration, update detection, and status monitoring.
 */

// Registration state
let registration = null;
let updateAvailable = false;

/**
 * Register the service worker
 * @returns {Promise<ServiceWorkerRegistration|null>}
 */
export async function registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
        console.warn('[SW] Service Workers not supported');
        return null;
    }

    try {
        registration = await navigator.serviceWorker.register('./sw.js', {
            scope: './',
        });

        console.log('[SW] Registered, scope:', registration.scope);

        // Set up update listener
        setupUpdateListener(registration);

        // Wait for service worker to be ready
        await navigator.serviceWorker.ready;
        console.log('[SW] Ready');

        // Check if we already have SharedArrayBuffer support
        if (hasSharedArrayBuffer()) {
            console.log('[SW] SharedArrayBuffer available');
        } else {
            console.warn('[SW] SharedArrayBuffer not available - reload may be needed');
        }

        return registration;
    } catch (error) {
        console.error('[SW] Registration failed:', error);
        throw error;
    }
}

/**
 * Check if SharedArrayBuffer is available
 * (indicates COOP/COEP headers are working)
 * @returns {boolean}
 */
export function hasSharedArrayBuffer() {
    try {
        new SharedArrayBuffer(1);
        return true;
    } catch {
        return false;
    }
}

/**
 * Set up listener for service worker updates
 */
function setupUpdateListener(reg) {
    reg.addEventListener('updatefound', () => {
        const newWorker = reg.installing;

        if (!newWorker) return;

        newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed') {
                if (navigator.serviceWorker.controller) {
                    // New version available
                    console.log('[SW] Update available');
                    updateAvailable = true;
                    showUpdateNotification();
                } else {
                    // First install
                    console.log('[SW] First install complete');
                }
            }
        });
    });

    // Listen for controller change (after skipWaiting)
    navigator.serviceWorker.addEventListener('controllerchange', () => {
        console.log('[SW] Controller changed');
        // Could auto-reload here, but better to let user decide
    });
}

/**
 * Show update notification banner
 */
function showUpdateNotification() {
    // Check if banner already exists
    if (document.querySelector('.sw-update-banner')) return;

    const banner = document.createElement('div');
    banner.className = 'sw-update-banner';
    banner.innerHTML = `
        <span>A new version is available.</span>
        <button class="sw-update-btn">Refresh</button>
        <button class="sw-dismiss-btn" aria-label="Dismiss">✕</button>
    `;

    // Style the banner
    Object.assign(banner.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        right: '0',
        padding: '12px 16px',
        background: 'var(--color-primary, #3b82f6)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '16px',
        zIndex: '10000',
        fontFamily: 'var(--font-sans, sans-serif)',
        fontSize: '14px',
    });

    const refreshBtn = banner.querySelector('.sw-update-btn');
    Object.assign(refreshBtn.style, {
        padding: '6px 16px',
        background: 'white',
        color: 'var(--color-primary, #3b82f6)',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontWeight: '500',
    });

    const dismissBtn = banner.querySelector('.sw-dismiss-btn');
    Object.assign(dismissBtn.style, {
        background: 'transparent',
        border: 'none',
        color: 'white',
        cursor: 'pointer',
        fontSize: '18px',
        padding: '4px',
    });

    // Event handlers
    refreshBtn.addEventListener('click', () => {
        applyUpdate();
    });

    dismissBtn.addEventListener('click', () => {
        banner.remove();
    });

    document.body.prepend(banner);
}

/**
 * Apply pending update
 */
export function applyUpdate() {
    if (registration?.waiting) {
        // Tell waiting service worker to skip waiting
        registration.waiting.postMessage({ type: 'SKIP_WAITING' });
    }
    // Reload the page
    window.location.reload();
}

/**
 * Check if an update is available
 * @returns {boolean}
 */
export function isUpdateAvailable() {
    return updateAvailable;
}

/**
 * Get the current service worker registration
 * @returns {ServiceWorkerRegistration|null}
 */
export function getRegistration() {
    return registration;
}

/**
 * Unregister the service worker
 */
export async function unregisterServiceWorker() {
    if (registration) {
        await registration.unregister();
        registration = null;
        console.log('[SW] Unregistered');
    }
}

/**
 * Clear the service worker cache
 */
export async function clearCache() {
    if (navigator.serviceWorker.controller) {
        return new Promise((resolve) => {
            const channel = new MessageChannel();
            channel.port1.onmessage = () => {
                console.log('[SW] Cache cleared');
                resolve();
            };
            navigator.serviceWorker.controller.postMessage(
                { type: 'CLEAR_CACHE' },
                [channel.port2]
            );
        });
    }
}

/**
 * Get service worker version
 */
export async function getVersion() {
    if (navigator.serviceWorker.controller) {
        return new Promise((resolve) => {
            const channel = new MessageChannel();
            channel.port1.onmessage = (event) => {
                resolve(event.data.version);
            };
            navigator.serviceWorker.controller.postMessage(
                { type: 'GET_VERSION' },
                [channel.port2]
            );
        });
    }
    return null;
}

// Export status checker
export const swStatus = {
    get isSupported() {
        return 'serviceWorker' in navigator;
    },
    get isRegistered() {
        return registration !== null;
    },
    get isActive() {
        return navigator.serviceWorker.controller !== null;
    },
    get hasSharedArrayBuffer() {
        return hasSharedArrayBuffer();
    },
    get updateAvailable() {
        return updateAvailable;
    },
};

export default {
    registerServiceWorker,
    hasSharedArrayBuffer,
    applyUpdate,
    isUpdateAvailable,
    getRegistration,
    unregisterServiceWorker,
    clearCache,
    getVersion,
    swStatus,
};
