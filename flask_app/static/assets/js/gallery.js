$.get("/get_images", data=>{
    const template = $("#thumbnail_card_template")
    data.forEach(image=>{
        let new_card = template.prop("content").cloneNode(true)
        $("a", new_card).attr("href", `${document.location.origin}/i/${image.uuid}`)
        $("h5", new_card).text(image.date)
        let img = $("img", new_card)
        img.attr("src", image.url)
        img.attr("alt", image.uuid)


        $("#link_container").append(new_card)
    })
})