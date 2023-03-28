$(function() {
    $('#submit').on('click', function(event) {
        event.preventDefault();
        const now = new Date();
        const dateStr = now.toLocaleDateString();
        const timeStr = now.toLocaleTimeString();
        var log = `## ${dateStr} ${timeStr}:\n`+ $('#log').val();
        // console.log($('#log').val())
        // console.log(log)
        $.ajax({
            url: '/v1/diary-log/addlog',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({content: log}),
            success: function(response) {

                var logList= $('#logList');
                response = JSON.parse(response)
                var pre = $('<pre></pre>');
                pre.text(response.content);
                logList.prepend(pre);
                
                // 清空 输入框
                $('#log').val('');
                // console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
    $.ajax({
        url: '/v1/diary-log/getlogs',
        type: 'GET',
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
            url: '/v1/diary-log/delete_all_log',
            type: 'GET',
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
