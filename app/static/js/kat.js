//function to validate ABN Number of sub-contractor
function validateABN(el){
    if(el.value.length > 11){
        el.value = el.value.substring(0,11)
    }
    else if(el.value.length < 11){
        el.style.border="none";
        el.style.boxShadow = "0px 0px 3px 1px  #cc3300";
        el.setCustomValidity(' ');
    }
    else if(el.value.length == 11){
        el.style.border = "1px solid lightgrey";
        el.style.boxShadow = "none";
        el.setCustomValidity('');
    }
    el.setCustomValidity('');
}

// function to validate contact number of the sub-contractor
function validate_contact(country, el){
    country_dict = {
        "+91": 10,
        "+61": 9
    }
    var len = country_dict[country];
    if (el.value.length > len)
        el.value = el.value.substring(0,len);
    else if (el.value.length < len){
        el.style.border="none";
        el.style.boxShadow = "0px 0px 3px 1px  #cc3300";
        el.setCustomValidity(' ');
    }
    else if(el.value.length == len){
        el.style.border = "1px solid lightgrey";
        el.style.boxShadow = "none";
        el.setCustomValidity('');
    }
}


// jQuery code for the app
$(document).ready(function(){
    height = $("#footer").height() + $(".navbar").height() + $(".head").height();
    window_height = $(window).height();
    new_height = window_height - height;
    $(".container-fluid").css({"min-height":new_height});
    // show the list by default( will be changed later on by the backend developer)
    for(i=0;i<13;i++)
        $(".items").append("<div class ='row mt-1'><div class='col-lg-12 bg-info'style='color:white;'><div class='row'><div class='col-sm-2 p-2'>"+i+"</div><div class='col-sm-9 p-2'>Job Title</div></div></div></div>");
    
    // going back to top 
    $(".back-to-top").click(function(){
        $("html, body").animate({ scrollTop: 0 }, "fast");
    });
    
});