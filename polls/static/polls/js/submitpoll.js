function myfunc(){
    var frm =$("#formsubmit");
    $.ajax({ 
        type: frm.attr('method'), // GET or POST
        url: frm.attr('action'), // the file to call
        data: frm.serialize(), // get the form data
        });
return false;
}