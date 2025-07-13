/**
 * Eisenhower Matrix Task Manager
 * Main JavaScript functionality
 */

// Get CSRF token from meta tag
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

// Settings Modal Functions
function openSettingsModal() {
    document.getElementById('settingsModal').classList.remove('hidden');
}

function closeSettingsModal() {
    document.getElementById('settingsModal').classList.add('hidden');
}

// Theme switching functionality
function setTheme(theme) {
    const body = document.body;
    if (theme === 'light') {
        body.classList.remove('bg-dark-300', 'text-gray-100');
        body.classList.add('bg-gray-100', 'text-gray-900');
        document.querySelectorAll('.bg-dark-200').forEach(el => {
            el.classList.remove('bg-dark-200');
            el.classList.add('bg-white');
        });
    } else {
        body.classList.remove('bg-gray-100', 'text-gray-900');
        body.classList.add('bg-dark-300', 'text-gray-100');
        document.querySelectorAll('.bg-white').forEach(el => {
            el.classList.remove('bg-white');
            el.classList.add('bg-dark-200');
        });
    }
}

// Share Links Management
function loadShareLinks() {
    const container = document.getElementById('shareLinksContainer');
    const noLinksMessage = document.getElementById('noShareLinksMessage');
    
    if (!container || !noLinksMessage) return; // Exit if elements don't exist (user not authenticated)
    
    fetch('/share-links')
        .then(response => response.json())
        .then(links => {
            if (links.length === 0) {
                noLinksMessage.classList.remove('hidden');
                return;
            }
            
            noLinksMessage.classList.add('hidden');
            container.innerHTML = '';
            
            links.forEach(link => {
                const linkElement = document.createElement('div');
                linkElement.className = 'bg-dark-100 rounded-lg p-3 flex flex-col';
                linkElement.dataset.linkId = link.id;
                
                const header = document.createElement('div');
                header.className = 'flex justify-between items-center mb-2';
                
                const title = document.createElement('h5');
                title.className = 'font-medium';
                title.textContent = link.name;
                
                const controls = document.createElement('div');
                controls.className = 'flex space-x-2';
                
                const copyBtn = document.createElement('button');
                copyBtn.className = 'text-blue-400 hover:text-blue-300';
                copyBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M8 2a1 1 0 000 2h2a1 1 0 100-2H8z" /><path d="M3 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v6h-4.586l1.293-1.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L10.414 13H15v3a2 2 0 01-2 2H5a2 2 0 01-2-2V5zM15 11h2a1 1 0 110 2h-2v-2z" /></svg>';
                copyBtn.addEventListener('click', function() {
                    copyShareLink(link.id);
                });
                
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'text-red-400 hover:text-red-300';
                deleteBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>';
                deleteBtn.addEventListener('click', function() {
                    deleteShareLink(link.id);
                });
                
                controls.appendChild(copyBtn);
                controls.appendChild(deleteBtn);
                
                header.appendChild(title);
                header.appendChild(controls);
                
                const info = document.createElement('div');
                info.className = 'text-sm text-gray-400';
                info.textContent = `Created: ${link.created_at} • Tasks: ${link.task_count}`;
                
                linkElement.appendChild(header);
                linkElement.appendChild(info);
                
                container.appendChild(linkElement);
            });
        })
        .catch(error => console.error('Error loading share links:', error));
}

function copyShareLink(linkId) {
    fetch(`/share-links/${linkId}/url`)
        .then(response => response.json())
        .then(data => {
            navigator.clipboard.writeText(data.url)
                .then(() => {
                    alert('Share link copied to clipboard!');
                })
                .catch(err => {
                    console.error('Could not copy text: ', err);
                });
        })
        .catch(error => console.error('Error getting share link URL:', error));
}

function createShareLink() {
    const nameInput = document.getElementById('shareLinkName');
    const name = nameInput.value.trim();
    
    if (!name) {
        alert('Please enter a name for the share link');
        return;
    }
    
    fetch('/share-links', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ name: name })
    })
    .then(response => response.json())
    .then(() => {
        nameInput.value = '';
        loadShareLinks();
    })
    .catch(error => console.error('Error creating share link:', error));
}

function deleteShareLink(linkId) {
    if (!confirm('Are you sure you want to delete this share link?')) {
        return;
    }
    
    fetch(`/share-links/${linkId}/delete`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(() => loadShareLinks())
    .catch(error => console.error('Error deleting share link:', error));
}

// Check if user is authenticated by looking for authenticated-only elements
function isAuthenticated() {
    return document.getElementById('settingsBtn') !== null;
}

// Document ready event handler
document.addEventListener('DOMContentLoaded', function() {
    // Load saved theme for all users
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        // Default theme is dark
        setTheme('dark');
    }

    // Only initialize authenticated user features if the user is authenticated
    if (isAuthenticated()) {
        // Initialize settings button
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', openSettingsModal);
        }
        
        // Initialize settings modal close if it exists
        const settingsModal = document.getElementById('settingsModal');
        if (settingsModal) {
            settingsModal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeSettingsModal();
                }
            });
        }
        
        // Initialize theme switching if theme options exist
        const themeOptions = document.querySelectorAll('.theme-option');
        if (themeOptions.length > 0) {
            // Update active state on theme button
            if (savedTheme) {
                const activeThemeBtn = document.querySelector(`.theme-option[data-theme="${savedTheme}"]`);
                if (activeThemeBtn) {
                    activeThemeBtn.classList.add('border-blue-500');
                    activeThemeBtn.classList.remove('border-transparent');
                }
            } else {
                // Default theme is dark
                const darkThemeBtn = document.querySelector('.theme-option[data-theme="dark"]');
                if (darkThemeBtn) {
                    darkThemeBtn.classList.add('border-blue-500');
                    darkThemeBtn.classList.remove('border-transparent');
                }
            }
            
            // Add click handlers to theme buttons
            themeOptions.forEach(button => {
                button.addEventListener('click', function() {
                    const theme = this.dataset.theme;
                    setTheme(theme);
                    
                    // Save theme preference to localStorage
                    localStorage.setItem('theme', theme);
                    
                    // Update active state on buttons
                    document.querySelectorAll('.theme-option').forEach(btn => {
                        btn.classList.remove('border-blue-500');
                        btn.classList.add('border-transparent');
                    });
                    this.classList.remove('border-transparent');
                    this.classList.add('border-blue-500');
                });
            });
        }
        
        // Add Task button functionality
        const addTaskBtn = document.getElementById('addTaskBtn');
        if (addTaskBtn) {
            addTaskBtn.addEventListener('click', function() {
                // If we're on the completed page, redirect to index and then open modal
                if (window.location.pathname.includes('completed')) {
                    localStorage.setItem('openAddTaskModal', 'true');
                    window.location.href = '/'; // Redirect to index
                } else if (typeof openAddTaskModal === 'function') {
                    // If we're already on the index page, just open the modal
                    openAddTaskModal();
                }
            });
        }
        
        // Check if we need to open the Add Task modal after redirect
        if (localStorage.getItem('openAddTaskModal') === 'true' && typeof openAddTaskModal === 'function') {
            openAddTaskModal();
            localStorage.removeItem('openAddTaskModal');
        }
        
        // Initialize share links
        loadShareLinks();
        
        // Initialize create share link button if it exists
        const createShareLinkBtn = document.getElementById('createShareLinkBtn');
        if (createShareLinkBtn) {
            createShareLinkBtn.addEventListener('click', createShareLink);
        }
    } else {
        // For unauthenticated users
        const loginRedirectBtn = document.getElementById('loginRedirectBtn');
        if (loginRedirectBtn) {
            loginRedirectBtn.addEventListener('click', function() {
                window.location.href = '/login';
            });
        }
    }
}); // End of DOMContentLoaded
