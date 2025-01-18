document.addEventListener('DOMContentLoaded', function() {
    // All DOM-related code is now safe to execute here

    let radioInputs = document.querySelectorAll('.frombox .radio-input .label input');
    let sentbutton = document.getElementById("animatedbutton");
    const languages=document.querySelector(".inputs");
    const sentButton = document.getElementById("sentbutton"); // Get the button
    sentButton.addEventListener('click', sentlanguge); 
    radioInputs.forEach(input => {
        input.addEventListener('click', () => {
            console.log(`Selected: ${input.id}`);
            document.querySelectorAll('.frombox .radio-input .label').forEach(label => {
                label.classList.remove('script-background');
            });

            input.parentElement.classList.add('script-background');
        });
    });

    function showLoadingIndicator() {
        const loadingDiv = document.querySelector("#loading-indicator");
        if (loadingDiv) {
            loadingDiv.style.display = "flex";
            languages.style.display="none";
        }
    }

    function hideLoadingIndicator() {
        const loadingDiv = document.querySelector("#loading-indicator");
        if (loadingDiv) {
            loadingDiv.style.display = "none";
        }
    }

    function sentlanguge() {
        console.log("Sending language...");

        const selectedLabel = document.querySelector('.frombox .radio-input .script-background');
        if (!selectedLabel) {
            console.error("Selected label not found!");
            return;
        }

        const selectedInput = selectedLabel.querySelector('input[type="radio"]');
        if (!selectedInput) {
            console.error("Selected input not found!");
            return;
        }

        const language = selectedInput.value;
        showLoadingIndicator();
        const urlParams = new URLSearchParams(window.location.search);
        const videoFilename = urlParams.get('video');

        if (!videoFilename) {
            console.error("No video filename found!");
            hideLoadingIndicator();
            return;
        }

        fetch("http://localhost:5001/language", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                language: language,
                video_filename: videoFilename
            }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            console.log("Language sent successfully!");
            return getSubtittel(language, videoFilename);
        })
        .catch(error => {
            console.error("Error sending language:", error);
            hideLoadingIndicator();
        });
    }



async function getSubtittel(language, videoFilename) {
    console.log("Fetching subtitle...");
    try {
        const response = await fetch(`http://localhost:5001/videoshow/${language}?video=${videoFilename}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            console.log("Processing complete:", data);
            hideLoadingIndicator();
            window.location.href = `/videoshow?video=${videoFilename}&subtitle=${encodeURIComponent(data.subtitleUrl)}`;
        } else {
            console.log("Processing not ready, retrying in 3 seconds...");
            setTimeout(() => getSubtittel(language, videoFilename), 3000);
        }
    } catch (error) {
        console.error("Error fetching subtitle:", error);
    }
}
});




















