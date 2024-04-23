
const jianguoyun_token = document.getElementById('jianguoyun_token');
const showTokenCheckbox = document.getElementById('showToken');

showTokenCheckbox.addEventListener('change', function() {
    if (showTokenCheckbox.checked) {
        jianguoyun_token.type = 'text';
    } else {
        jianguoyun_token.type = 'password';
    }
});


// 发送GET请求以获取配置信息并填充输入框
function getJianguoyunConfig() {
    $.ajax({
        url: '/v1/diary-log/get-jianguoyun-account',
        type: 'GET',
        success: function(response) {
            var jsonResponse = JSON.parse(response);
            // 请求成功处理
            $('#jianguoyun_account').val(jsonResponse.jianguoyun_account);
            $('#jianguoyun_token').val(jsonResponse.jianguoyun_token);
            // $('#jianguoyun_current_sync_file').val(jsonResponse.current_sync_file);
            // $('#jianguoyun_other_sync_file_list').val(jsonResponse.other_sync_file_list);
        },
        error: function(xhr, status, error) {
            // 请求失败处理
            console.error('Failed to get github config:', error);
        }
    });
}

getJianguoyunConfig();

$('#jianguoyun-save-changes-and-test-connection').click(function() {
    // 收集输入框的值
    var jianguoyun_account = $('#jianguoyun_account').val();
    var jianguoyun_token = $('#jianguoyun_token').val();
    // var jianguoyun_current_sync_file = $('#jianguoyun_current_sync_file').val();
    // var jianguoyun_other_sync_file_list = $('#jianguoyun_other_sync_file_list').val();

    // 创建要发送的数据对象
    var data = {
        jianguoyun_account: jianguoyun_account,
        jianguoyun_token: jianguoyun_token,
        // jianguoyun_current_sync_file: jianguoyun_current_sync_file,
        // jianguoyun_other_sync_file_list: jianguoyun_other_sync_file_list
    };

    // 发送 POST 请求
    $.ajax({
        url: '/v1/diary-log/jianguoyun-config',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            var jsonResponse = JSON.parse(response);
            if (jsonResponse.success === 1) {
                alert("Success");
            }
            else if (jsonResponse.current_sync_file_flag ===0){
                alert("current_sync_file is null")
            }
            else if (jsonResponse.jianguoyun_account ===0){
                alert("input jianguoyun_account is null")
            }
            else if (jsonResponse.jianguoyun_token ===0){
                alert("input jianguoyun_token is null")
            }
            else if (jsonResponse.test_jianguoyun_access ===0){
                alert("Test jianguoyun connection is failed, try again")
            }
            else{alert("Failed, please check your configuration")}
        },
        error: function(xhr, status, error) {
            // 请求失败处理
            console.error('Failed to save changes:', error);
        }
    });
});