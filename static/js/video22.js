// Gets video name from URL
const urlParams = new URLSearchParams(window.location.search);
const videoName = urlParams.get('video');
console.log("videoName", videoName);
const videoTag = document.getElementById('video-tag');
const loader = document.querySelector('.loader');

if (videoName) {
    // Show loader
    if (loader) loader.style.display = 'block';
    
    // Set video source
    videoTag.src = 'http://localhost:5001/video/' + videoName;
    
    // Handle video loading events
    videoTag.addEventListener('loadeddata', () => {
        if (loader) loader.style.display = 'none';
        document.querySelector('.vedios').style.display = 'flex';
        document.querySelector('.inputs').style.display = 'none';
    });

    videoTag.addEventListener('error', () => {
        alert('Error loading video. Please try again.');
        if (loader) loader.style.display = 'none';
    });
} else {
    alert('No video found in the URL!');
}