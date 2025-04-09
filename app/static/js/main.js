document.addEventListener('DOMContentLoaded', () => {
    // Copy list URL functionality
    const copyUrlButton = document.getElementById('copy-url-button');
    if (copyUrlButton) {
        copyUrlButton.addEventListener('click', () => {
            const currentUrl = window.location.href;
            navigator.clipboard.writeText(currentUrl)
                .then(() => showCopiedFeedback())
                .catch(err => console.error('Could not copy text: ', err));
        });
    }

    // Copy list code functionality
    const copyCodeButtons = document.querySelectorAll('.copy-code-button');
    copyCodeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const code = button.getAttribute('data-code');
            navigator.clipboard.writeText(code)
                .then(() => showCopiedFeedback())
                .catch(err => console.error('Could not copy text: ', err));
        });
    });

    // List name editing
    const editNameButton = document.getElementById('edit-list-name');
    const cancelEditButton = document.getElementById('cancel-edit-name');
    const nameDisplay = document.getElementById('list-name-display');
    const nameEditForm = document.getElementById('list-name-edit-form');
    
    if (editNameButton && cancelEditButton && nameDisplay && nameEditForm) {
        editNameButton.addEventListener('click', () => {
            nameEditForm.classList.remove('hidden');
            nameEditForm.querySelector('input[name="name"]').focus();
        });
        
        cancelEditButton.addEventListener('click', () => {
            nameEditForm.classList.add('hidden');
        });
    }

    // Recent list navigation
    const recentListItems = document.querySelectorAll('.recent-list-item');
    if (recentListItems.length > 5) {
        // Limit to 5 items if there are more for some reason
        for (let i = 5; i < recentListItems.length; i++) {
            recentListItems[i].style.display = 'none';
        }
    }
    
    recentListItems.forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON') {
                const url = item.getAttribute('href');
                if (url) {
                    const code = url.split('/').pop();
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = `/lists/join`;
                    
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'code';
                    input.value = code;
                    
                    form.appendChild(input);
                    document.body.appendChild(form);
                    form.submit();
                }
            }
        });
    });

    // Add new item form submission animation
    const addItemForm = document.getElementById('add-item-form');
    if (addItemForm) {
        addItemForm.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            }
        });
    }

    // Toggle item completion with animation
    const toggleButtons = document.querySelectorAll('.toggle-item');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            const itemContent = form.closest('.item').querySelector('.item-content');
            
            // Add transition class for animation
            itemContent.classList.add('transition-opacity');
            itemContent.style.opacity = '0.5';
            
            // Submit the form
            form.submit();
        });
    });

    // Delete item confirmation
    const deleteButtons = document.querySelectorAll('.delete-item');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            form.submit();
        });
    });

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const listItems = document.querySelectorAll('.list-item');
            
            listItems.forEach(item => {
                const title = item.querySelector('.list-title').textContent.toLowerCase();
                const code = item.querySelector('.list-meta').textContent.toLowerCase();
                if (title.includes(query) || code.includes(query)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
});

// Show copied feedback notification
function showCopiedFeedback() {
    let feedback = document.querySelector('.copied-feedback');
    
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'copied-feedback';
        feedback.textContent = 'Copied to clipboard!';
        document.body.appendChild(feedback);
    }
    
    // Remove existing animation class if present
    feedback.classList.remove('show-copied-feedback');
    
    // Trigger reflow to restart animation
    void feedback.offsetWidth;
    
    // Add animation class
    feedback.classList.add('show-copied-feedback');
} 