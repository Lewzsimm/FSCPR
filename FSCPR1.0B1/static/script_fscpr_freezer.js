
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

const add_btn = document.querySelector(".add_btn--freezer");
const add_headers = document.querySelector(".new_items_container--top")
const add_headers_on = document.querySelector(".new_items_container--top__on")
const fields_container = document.getElementById("new_body")



let i = 0;
let j = 0;
let k = 0;

add_btn.addEventListener("click", function() {
    if (add_headers.classList.contains("new_items_container--top")) {
        add_headers.classList.remove("new_items_container--top");
        add_headers.classList.add("new_items_container--top__on");
    };

    // Create row, td, and td contents
        const row = document.createElement("tr");
        row.setAttribute("Id", "row"+i);
        row.setAttribute("class", "row" + i);
        
        let t_data = document.createElement("td");
        t_data.setAttribute("Id", "t_data"+j);
      
        const new_shelf = document.createElement("input");
        new_shelf.type = "number";
        new_shelf.name = "shelf_new";
        new_shelf.id = "shelf_new" + i;
        new_shelf.setAttribute("class", "shelf_ud_freezer");
        new_shelf.setAttribute("value", "0");

        const new_name = document.createElement("input");
        new_name.type = "text";
        new_name.name = "name_new";
        new_name.setAttribute("class", "name_ud")
        new_name.setAttribute("value", "")

        const new_brand = document.createElement("input");
        new_brand.type = "text";
        new_brand.name = "brand_new";
        new_brand.setAttribute("class", "brand_ud");
        new_brand.setAttribute("value", "");

        // Create a current date variable for default production dates
        
        const date = new Date();
        let day = date.getDate();
        let month = date.getMonth() + 1;
        let year = date.getFullYear();
        let current_date = `${year}-${date_format(month)}-${date_format(day)}`;
        
        // Create a current date variable with + 5 days added for default expiry dates
        let day_5 = date.getDate() + 5;
        let current_date_5 = `${year}-${date_format(month)}-${date_format(day_5)}`;
        
        // Function for adding 0 before # if < 10
        function date_format(day){
            if (day < 10) {
                day = "0"+ day;
                return day;
            } 
            return day;
        };
        
        const new_production = document.createElement("input");
        new_production.type = "date";
        new_production.name = "production_new";
        new_production.setAttribute("class", "production_ud_freezer");
        new_production.setAttribute("value", current_date);
        console.log(date_format(current_date));

        const new_date = document.createElement("input");
        new_date.type = "date";
        new_date.name = "date_new";
        new_date.setAttribute("class", "exp_ud_freezer");
        new_date.setAttribute("value", current_date_5);
        console.log(date_format(day_5));

        const new_portions = document.createElement("input");
        new_portions.type = "number";
        new_portions.name = "portions_new";
        new_portions.setAttribute("class", "ptns_ud_freezer")
        new_portions.setAttribute("min", "0")
        new_portions.setAttribute("value", "0")

        const new_batches = document.createElement("input");
        new_batches.type = "text";
        new_batches.name = "batches_new";
        new_batches.setAttribute("class", "batches_ud_freezer")
        new_batches.setAttribute("min", "0.0")
        new_batches.setAttribute("value", "0")

        const new_batch_size = document.createElement("input");
        new_batch_size.type = "text";
        new_batch_size.name = "batch_size_new";
        new_batch_size.setAttribute("class", "batch_size_ud_freezer")
        new_batch_size.setAttribute("min", "0.0")
        new_batch_size.setAttribute("value", "1")

    // The siblings for select must be created after it in the stack and are below, as they need the added select's Id 
        const new_select = document.createElement("select");
        new_select.type = "text";
        new_select.name = "select_new";
        new_select.id = "select_new" + i;
        new_select.setAttribute("class", "prep_ud_freezer")

        const new_today = document.createElement("input");
        new_today.type = "hidden";
        new_today.name = "today_new";
        new_today.setAttribute("value", "Today")

        const new_user = document.createElement("input");
        new_user.type = "hidden";
        new_user.name = "user_new";
        new_user.setAttribute("value", "User")

        const option_on = document.createElement("option");
        option_on.value = "on";
        option_on.text = "On";

        const option_off = document.createElement("option");
        option_off.value = "off";
        option_off.text = "-";

        const new_remove = document.createElement("button");
        new_remove.type = "button";
        new_remove.name = "remove_new";
        new_remove.id = "remove_new" + i;
        new_remove.innerText = "X";
        new_remove.setAttribute("class", "discard_ud_freezer");

// Remove row on click, and remove headers if empty
        let tr_remove = document.getElementById("remove_new" + i);
        new_remove.addEventListener("click", function(tr_remove) {
            console.log(tr_remove);
            this.parentElement.parentElement.remove();
            k--;
            console.log(i);
            console.log(k, "k");
            if (k == 0){
                add_headers.classList.remove("new_items_container--top__on");
                add_headers.classList.add("new_items_container--top");
            }
            });

    // Add row to table      
        fields_container.appendChild(row);      
        let added_row = document.getElementById("row"+(i));

// Function for adding td and cell content, get new row's Id, then append a new td; 
// finally, Get new td's Id, then add cell contents to it
        function fill_cell(j, child){
            let t_data = document.createElement("td");
            t_data.setAttribute("Id", "t_data"+j);
            added_row.appendChild(t_data);
            let added_td = document.getElementById("t_data"+(j));
            added_td.appendChild(child);
        }
        // Repeat adding td and cell content
        fill_cell(j, new_shelf);
        j++;
        fill_cell(j, new_name);
        j++;
        fill_cell(j, new_brand);
        j++;
        fill_cell(j, new_production);
        j++;
        fill_cell(j, new_date);
        j++;
        fill_cell(j, new_portions);
        j++;
        fill_cell(j, new_batches);
        j++;
        fill_cell(j, new_batch_size);
        j++;
        fill_cell(j, new_select);
        let select_id = "select_new" + i;
        select_tag = document.getElementById(select_id);
        select_tag.appendChild(option_off);
        select_tag.appendChild(option_on);
        j++;
        added_row.appendChild(new_today);
        j++;
        added_row.appendChild(new_user);
        j++;
        fill_cell(j, new_remove);
        j++;
        i++;
        k++;
        console.log(i);

        let s_button = document.getElementById("s_button");
        s_button.addEventListener("click", function(){
        input.submit.apply(shelf_new);

        });
});