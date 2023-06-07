ckan.module('stats_by_date', function ($) {
    stats_by_date_submission_btn = $(".stats_by_date_submission_btn")
    start_date_input = $("#pull-stats-starting-date")
    end_date_input = $("#pull-stats-ending-date")


    return{
        initialize: function(){
            stats_by_date_submission_btn.on("click",function(){
                let start_date = start_date_input.val()
                let end_date = end_date_input.val()
                if(new Date(start_date) > new Date(end_date)){
                    fetch(`${this.window.origin}/stats/pull_stats_by_date`,{
                        method:"POST",
                        headers:{"Accept":"application/json","Content-Type":"application/json"},
                        body:JSON.stringify({"state":"invalid"})
                    })
                    return
                }
                fetch(`${window.location.origin}/stats/pull_stats_by_date`, {
                    method:"POST",
                    headers:{
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body:JSON.stringify(
                        {
                            "state": "valid",
                            "start_date": start_date,
                            "end_date":end_date
                        }
                        )
                }).then(res=>res.json()).then(data=>{
                    let frame = document.createElement("iframe")
                    frame.src = window.location.origin
                    frame.srcdoc = data.table
                    document.body.appendChild(frame);

                    frame.onload = function(){
                        frame.style.display = "none"
                        let frameWindow = frame.contentWindow
                        frameWindow.focus()
                        frameWindow.print()
                    }
                })
            })
        }
    }
})
