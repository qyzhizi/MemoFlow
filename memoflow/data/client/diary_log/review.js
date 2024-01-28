$(function() {
    $.ajax({
        url: '/v1/diary-log/get_review_logs',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        },
        success: function(response) {
            // console.log(response);
            response = JSON.parse(response)
            for (var i = 0; i < response.logs.length; i++) {
                var log = response.logs[i];
                var pre = $('<pre></pre>');
                pre.text(log);
                $('#logList').prepend(pre);
            }
        },
        error: function(error) {
            console.log(error);
        }
    });

    $('#delete_all').on('click', function(event) {
        event.preventDefault();
        // var log = $('#log').val();
        $.ajax({
            url: '/v1/diary-log/delete_all_review_log',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
            },
            success: function(response) {
                var logList= $('#logList');
                logList.html("");
                // console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
 
});
