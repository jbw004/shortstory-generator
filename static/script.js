function generateStory() {
    const circumstance = document.getElementById('circumstance').value;
    const protagonist = document.getElementById('protagonist').value;
    const comicContainer = document.getElementById('comicContainer');
    const dialogueElement = document.getElementById('dialogue');
    const generateButton = document.getElementById('generateButton');

    if (!circumstance || !protagonist) {
        alert('Please enter a circumstance and select a protagonist.');
        return;
    }

    comicContainer.innerHTML = '';
    dialogueElement.textContent = 'Generating...';
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
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.panels && data.panels.length > 0) {
            data.panels.forEach((panel, index) => {
                const panelElement = document.createElement('div');
                panelElement.className = 'comic-panel';
                const img = document.createElement('img');
                img.src = panel.url;
                img.alt = `Panel ${index + 1}`;
                panelElement.appendChild(img);
                comicContainer.appendChild(panelElement);
            });
        }
        if (data.dialogue) {
            dialogueElement.innerHTML = formatDialogue(data.dialogue);
        }
        generateButton.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        dialogueElement.textContent = `An error occurred: ${error.message}. Please try again.`;
        generateButton.disabled = false;
    });
}

function formatDialogue(dialogue) {
    // Split the dialogue into panels
    const panels = dialogue.split('\n\n');
    let formattedDialogue = '';

    panels.forEach((panel, index) => {
        formattedDialogue += `<div class="panel">
            <h3>Panel ${index + 1}</h3>
            ${panel.replace(/\n/g, '<br>')}
        </div>`;
    });

    return formattedDialogue;
}

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