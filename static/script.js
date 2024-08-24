function generateStory() {
    const circumstance = document.getElementById('circumstance').value;
    const protagonist = document.getElementById('protagonist').value;
    const storyElement = document.getElementById('story');
    const generateButton = document.getElementById('generateButton');

    if (!circumstance || !protagonist) {
        alert('Please enter a circumstance and select a protagonist.');
        return;
    }

    storyElement.textContent = 'Generating story...';
    generateButton.disabled = true;

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'circumstance': circumstance,
            'protagonist': protagonist
        })
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        storyElement.textContent = '';  // Clear the "Generating story..." message

        function readChunk() {
            return reader.read().then(({ done, value }) => {
                if (done) {
                    console.log('Stream complete');
                    generateButton.disabled = false;
                    return;
                }
                const chunk = decoder.decode(value);
                storyElement.textContent += chunk;
                storyElement.scrollTop = storyElement.scrollHeight;  // Auto-scroll to the bottom
                return readChunk();
            });
        }

        return readChunk();
    }).catch(error => {
        console.error('Error:', error);
        storyElement.textContent = `An error occurred while generating the story: ${error.message}. Please try again.`;
        generateButton.disabled = false;
    });
}

// ... (keep the rest of the file as it is) ...

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('storyForm');
    if (form) {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            generateStory();
        });
    } else {
        console.error('Story form not found');
    }
});

console.log('Script loaded');