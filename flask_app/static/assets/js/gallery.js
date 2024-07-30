$.get("/get_uuids", data=>{
    data.forEach(uuid=>{
        $("#link_container").append(`<a href="${document.location.origin}/i/${uuid}">${uuid}</a><br>`)
    })
})