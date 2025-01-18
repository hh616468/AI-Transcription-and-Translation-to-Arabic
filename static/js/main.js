const videoSrc=document.getElementById("source-video")
// const videoInput=document.getElementById('videoInput');
const videoinput=document.getElementById("videoInput")
const submit=document.querySelector(".submit");
const video=document.querySelector(".videos video");
const submit2=document.getElementById("animatedbutton");

const heder=document.querySelector(".header");
const footer=document.querySelector(".footer");
const wrapper=document.querySelector(".wrapper .content")
const usecases=document.querySelector(".usecases")
const about=document.querySelector(".about")

if (videoinput) {
  videoinput.addEventListener('change', function() {
    if (videoinput.files.length > 0) {
      console.log(videoinput)
      submit2.style.display = "flex";
   
    }
  });
}

if (submit2) {
  submit2.addEventListener("click", (e) => {
    uploadVideo();
  });
}

function showLoadingIndicator() {
  const loadingDiv = document.querySelector("#loading-indicator");
  if (loadingDiv) {
      loadingDiv.style.display = "flex";
      heder.style.display="none";
      wrapper.style.display="none";
      usecases.style.display="none";
      about.style.display="none";
      footer.style.display="none";
  }
}

function hideLoadingIndicator() {
  const loadingDiv = document.querySelector("#loading-indicator");
  if (loadingDiv) {
      loadingDiv.style.display = "none";
  }
}

// هنا اشياء الفيديو 

function uploadVideo() {
  if (!videoinput || !videoinput.files[0]) {
    return;
  }
  const formData = new FormData();
  
  formData.append('video', videoinput.files[0]);
  showLoadingIndicator()
  fetch('http://localhost:5001/index', {
    method: 'POST',
    body: formData
  })
    .then(response => 
      {
        return response.json()
      })
    .then(data => {
        console.log('Response from server:', data);
        if (data.success) {
            console.log('Redirecting to:', '/edetvido?video=' + data.filename);
            window.location.href = '/edetvido?video=' + data.filename;
        } else {
            alert('Upload failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error during upload:', error);
        alert('Upload failed: ' + error);
    });
}