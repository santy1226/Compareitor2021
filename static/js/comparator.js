function checkFiles(){
    if (files.files.length != 2){
        alert("You need to upload exactly 2 files to proceed with the comparison.");
        files.value = null;
    }
}

function doClick(){
    files = document.getElementById("selector");
    files.click()
}

function load(){
    files = document.getElementById("selector");
    button = document.getElementById("button");
    button.addEventListener('click', doClick);
    files.addEventListener('change', checkFiles);
}

function markText(load, data){
    var text = data.split('#');
    if (load.toLowerCase() == "true"){
        $('textarea').highlightTextarea({
            words: text,
            color: '#d2e8ff'
        });
    }else {
        alert("No files have been uploaded!")
    }
}


window.onload = load();



