document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const videoFilename = urlParams.get('video');
    const subtitleUrl = urlParams.get('subtitle');

    const video = document.getElementById('video-tag'); // Get video element
    const subtitleTrack = document.getElementById('subtitletrack'); // Get track element
    console.log("mew , mew" , subtitleTrack);
    if (videoFilename) {
        // Set video source (you might need to adjust the path)
        document.getElementById('source-video').src = `/uploads/${videoFilename}`;
    }

    if (subtitleUrl) {
        // Set subtitle track source
        subtitleTrack.src = subtitleUrl;
        console.log("hoof" , subtitleTrack.src);
    }

    // Optional: If you need to "activate" the subtitles
    // video.textTracks[0].mode = 'showing';

    // Add any other logic for controlling the video here (play/pause, etc.)
});