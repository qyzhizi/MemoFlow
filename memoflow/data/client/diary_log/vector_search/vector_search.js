$(function() {
    window.search = function() {
        // Get the value from the textarea
        var query = $('#query').val();
        if (query === "") {
            return;
        }
        $.ajax({
            url: '/v1/diary-log/search-contents-from-vecter-db',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({search_data: query}),
            success: function(response) {
                response = JSON.parse(response)
                var length = response.search_result.length
                for (var i = 0; i < length; i++) {
                    var item = response.search_result[length-1-i];
                    var pre = $('<pre></pre>');
                    pre.text(item);
                    $('#result').prepend(pre);

                }
                var query_pre = $('<pre></pre>');
                query_pre.text(query);
                query_pre.css("border", "1px solid blue"); // 设置边框颜色为红色
                $('#result').prepend(query_pre);
                // 清空 输入框
                $('#query').val('');
            },
            error: function(error) {
                console.log(error);
            }
        });
    }
    $('#init_vector_db').on('click', function(event) {
        event.preventDefault();
        // ask for confirmation
        if (!confirm("Are you sure to init vector db?")) {
            return;
        }
        $.ajax({
            url: '/v1/diary-log/update_all_que_to_vector_db',
            type: 'PUT',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
            },
            success: function(response) {
                console.log(response);
                // pop up a dialog
                alert(response);
                // reload the page
                window.location.reload();
            },
            error: function(error) {
                // pop up a dialog
                alert(error);
                console.log(error);
            }
        });
    });
});
