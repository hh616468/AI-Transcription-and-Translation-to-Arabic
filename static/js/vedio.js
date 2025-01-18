let inputcolor = document.getElementById("color");
let inputrange = document.getElementById("size");
let selectedfont = document.getElementById("select");
let checkbox = document.getElementById("checkbox");
let transcription = document.querySelector(".video-label");



let style = document.createElement("style");
document.head.appendChild(style);

let styleProperties = {
    color: "#ffffff",
    fontSize: "25px", 
    fontFamily: "'Courier New', Courier, monospace", 
    backgroundColor: "transparent",
};

const updateStyle = () => {
    style.textContent = `
        .video-label::cue {
            color: ${styleProperties.color};
            font-size: ${styleProperties.fontSize};
            font-family: ${styleProperties.fontFamily};
            background-color: ${styleProperties.backgroundColor};
        }
    `;
};

inputcolor.addEventListener("change", (e) => {
    styleProperties.color = inputcolor.value;
    updateStyle();
});

inputrange.addEventListener("change", (e) => {
    styleProperties.fontSize = `${inputrange.value}px`;
    updateStyle();
});

checkbox.addEventListener("change", (e) => {
    if (checkbox.checked) {
        styleProperties.backgroundColor = `#0000009c`;
    } else {
        styleProperties.backgroundColor = "transparent"; 
    }
    updateStyle();
});

selectedfont.addEventListener("change", (e) => {
    let selectedValue = selectedfont.options[selectedfont.selectedIndex].value;
    if (selectedValue === "1") {
        styleProperties.fontFamily = "'Courier New', Courier, monospace";
    } 
    else if (selectedValue === "2") {
        styleProperties.fontFamily = "'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif";
    } 
    else if (selectedValue === "3") {
        styleProperties.fontFamily = "'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif";
    } 
    else if (selectedValue === "4") {
        styleProperties.fontFamily = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    }
    updateStyle();
});
updateStyle();






let color=document.getElementById("4");
let reange=document.getElementById("9");
let font=document.getElementById("25");
let swit=document.getElementById("36");
let is=document.querySelectorAll(".in-icon i");
let arrayofid=[color.id,reange.id,font.id,swit.id];
let arrayofelement=[color,reange,font,swit];
Array.from(is).forEach(e=>{    
    e.addEventListener("click",()=>{
        Array.from(is).forEach(d=>{
            d.classList.remove("click-icon");
                arrayofelement.forEach(ee=>{
                    ee.classList.remove("return");
                })
        })
        e.classList.add("click-icon");
            for(let i=0;i<=arrayofid.length;i++){
                if(e.id*e.id == arrayofid[i]){
                arrayofelement[i].classList.add("return");
            }
        }
    })
})





