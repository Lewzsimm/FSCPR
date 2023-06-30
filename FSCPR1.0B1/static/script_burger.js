const burg_link = document.querySelector(".burger__box");
const burg_box = document.querySelector(".burger__links--box");
const burg_logo = document.querySelector(".burger__logo");

burg_link.addEventListener("click", function() {
    if (burg_box.classList.contains("burger__links--box--open")){
        burg_box.classList.remove("burger__links--box--open");
    }else{
        burg_box.classList.add("burger__links--box--open");
    }
    if (burg_logo.classList.contains("burger__nav--open")){
        burg_logo.classList.remove("burger__nav--open");
    }else{
        burg_logo.classList.add("burger__nav--open");
    }
});