function activeLogin(){
    document.getElementById("usernameLogin").required = true;
    document.getElementById("passLogin").required = true;

    document.getElementById("usernameRegister").required = false;
    document.getElementById("nameRegister").required = false;
    document.getElementById("passRegister").required = false;

    document.getElementById("mode").value = "login";
}

function activeRegister(){
    document.getElementById("usernameRegister").required = true;
    document.getElementById("nameRegister").required = true;
    document.getElementById("passRegister").required = true;

    document.getElementById("usernameLogin").required = false;
    document.getElementById("passLogin").required = false;

    document.getElementById("mode").value = "register";
}

document.getElementById("tab1").addEventListener('click', activeLogin);
document.getElementById("tab2").addEventListener('click', activeRegister);
