document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        // Hide error message
        errorMessage.style.display = 'none';
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Redirect to chat page
                window.location.href = '/chat';
            } else {
                // Show error message
                errorMessage.textContent = data.error || 'Invalid credentials';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            console.error('Login error:', error);
            errorMessage.textContent = 'Connection error. Please try again.';
            errorMessage.style.display = 'block';
        }
    });
    
    // Clear error message when user types
    document.getElementById('username').addEventListener('input', function() {
        errorMessage.style.display = 'none';
    });
    
    document.getElementById('password').addEventListener('input', function() {
        errorMessage.style.display = 'none';
    });
});