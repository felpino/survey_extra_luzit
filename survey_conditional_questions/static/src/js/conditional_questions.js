odoo.define('survey_confitional_questions.surveys', function (require) {
    "use strict";

    require('web.dom_ready');
    //var framework = require("web.framework");
    

    function checkConditional(obj, text) {
      
       if(window.location.href.indexOf("/survey/fill") < 0){
        return Promise.resolve([]);
       };

       if(  !$("[name='token']") || !$("[name='token']")[0] ||  !$("[name='token']")[0].value){
        return Promise.resolve([]);
       }

       $.blockUI({ message : "Espere un momento..."});

        let objs_radio = [];
        $('.check_conditional_radio').each(function () {
            let $currentJqueryElement = $(this)[0];
            if ($currentJqueryElement.checked) {
                let json = {};
                json[$currentJqueryElement.name] = $currentJqueryElement.value;
                objs_radio.push(json);
            }

        });


        let objs_check = [];
        $('.check_conditional_checkbox').each(function () {
            let $currentJqueryElement = $(this)[0];
            if ($currentJqueryElement.checked) {
                let json = {};
                json[$currentJqueryElement.name] = $currentJqueryElement.value;
                objs_check.push(json);
            }
        });

        

        
        //console.log("obj==>", "A", obj, "B",obj.target,"C" , obj[0].target,"D", obj.name,"F", obj[0].name);
        //console.log(objs_radio.concat(objs_input).concat(objs_check));

        return new Promise((resolve, reject) => {
            $.ajax({
                type: "POST",
                url: "/survey_extra/get_conditional",
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify({
                    "params": {
                        "page_id": $("[name='page_id']")[0].value, 
                        "token": $("[name='token']")[0].value,
                        "ids_idq": obj.target ? obj.target.name : obj[0].name,
                        "alldata": objs_radio.concat(objs_check)
                    }
                }),
                success: function (data) {
                    resolve(data.result);
                    $.unblockUI();
                },
                error: ()=>{
                    $.unblockUI();
                }
            });;

        });
    }
    // Get the input box

    // Init a timeout variable to be used below
    var timeout = null;

    $(".check_conditional_radio").on("click", function (e) {
        checkConditional(e, false).then((r) => {
            if (r && r.length >= 0 && r[0] != "no_conditional") {
                for (let x = 0; x <= r.length - 1; x++) {
                    let spl = r[x].split(":");

                    if (spl[1] == "hide") {
                        $("#" + spl[0]).addClass("collapse")
                        $("#" + spl[0]).find('input:text, input:password, input[type="number"]').each(function () {
                            $(this).val('');
                        });
                        $("#" + spl[0]).find('textarea').not(".cascade-textarea").each(function () {
                            $(this).val('');
                        });
                        $("#" + spl[0]).find('label').removeClass('active').end().find('[type="radio"]').prop('checked', false);
                        $("#" + spl[0]).find('label').removeClass('active').end().find('[type="checkbox"]').prop('checked', false);
                        $(`[name*='${spl[0]}']`).each(function () {
                            console.log("THIS 1==>", this);
                            $(this).prop('required',false);
                        });
                    } else {
                        $("#" + spl[0]).removeClass("collapse")
                        $(`[name*='${spl[0]}']`).each(function () {
                            console.log("THIS 2==>", this);
                            $(this).prop('required',false);
                        });
                    }
                }

            }
        });
    });

    $(".check_conditional_checkbox").on("click", function (e) {
        checkConditional(e, false).then((r) => {
            if (r && r.length >= 0 && r[0] != "no_conditional") {
                for (let x = 0; x <= r.length - 1; x++) {
                    let spl = r[x].split(":");

                    if (spl[1] == "hide") {
                        $("#" + spl[0]).addClass("collapse")
                        $("#" + spl[0]).find('input:text, input:password, input[type="number"]').each(function () {
                            $(this).val('');
                        });
                        $("#" + spl[0]).find('textarea').not(".cascade-textarea").each(function () {
                            $(this).val('');
                        });
                        $("#" + spl[0]).find('label').removeClass('active').end().find('[type="radio"]').prop('checked', false);
                        $("#" + spl[0]).find('label').removeClass('active').end().find('[type="checkbox"]').prop('checked', false);
                        $(`[name*='${spl[0]}']`).each(function () {
                            console.log("THIS==> 3", this);
                            $(this).prop('required',false);
                        });
                    } else {
                        $("#" + spl[0]).removeClass("collapse")
                        $(`[name*='${spl[0]}']`).each(function () {
                            console.log("THIS==> 4", this);
                            $(this).prop('required',false);
                        });
                    }
                }
            }
        });
    });


    checkConditional($(".js_surveyform")).then((r) => {
        if (r && r.length >= 0 && r[0] != "no_conditional") {
            for (let x = 0; x <= r.length - 1; x++) {
                let spl = r[x].split(":");
                if (spl[1] == "hide") {
                    $("#" + spl[0]).addClass("collapse")
                    $("#" + spl[0]).find('input:text, input:password, input[type="number"]').each(function () {
                        $(this).val('');
                    });

                    $("#" + spl[0]).find('textarea').not(".cascade-textarea").each(function () {
                        $(this).val('');
                    });
                    $("#" + spl[0]).find('label').removeClass('active').end().find('[type="radio"]').prop('checked', false);
                    $("#" + spl[0]).find('label').removeClass('active').end().find('[type="checkbox"]').prop('checked', false);
                    $(`[name*='${spl[0]}']`).each(function () {
                        $(this).prop('required',false);
                    });

                } else {
                    $("#" + spl[0]).removeClass("collapse");
                    $(`[name*='${spl[0]}']`).each(function () {
                        console.log("THIS 6==>", this);
                        $(this).prop('required',true);
                    });
                }
            }
        }
    });

});
