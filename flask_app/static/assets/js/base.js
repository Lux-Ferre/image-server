if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    $("html").attr("data-bs-theme", "light")
}

if(document.cookie.includes("username")){
    $("#nav_login").addClass("d-none")
    $("#nav_logout").removeClass("d-none")
} else {
    $("#nav_login").removeClass("d-none")
    $("#nav_logout").addClass("d-none")
}