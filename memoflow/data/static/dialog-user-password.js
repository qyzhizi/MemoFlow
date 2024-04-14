import {
    showoff_class,
    showNotification
} from '/v1/diary-log/static/utils.js';


$('body').on('click', '#close-password-edit, #cancel-password-info-edit', 
    function() {
        // debugger;
        showoff_class("dialog-wrapper change-password-dialog showup")
});


$('body').on('click', '#save-password-info-edit', function() {
    // debugger;
    // 获取具有特定 id 的输入元素
    let new_password_value =  $('#dialog-new-password').val();
    var repeat_password_value = $('#dialog-repeat-password').val();
    if (new_password_value === '' || repeat_password_value === '') {
        alert('输入为空!');
        return;
    }
    if (new_password_value != repeat_password_value) {
        alert('两次密码不一致!');
        return;
    }

    let data = {
        new_password: new_password_value,
        repeat_password: repeat_password_value
    };
    // Convert the object to a JSON string
    let jsonData = JSON.stringify(data);

    var url = '/v1/diary-log/set-user-password-info';
    // 发送 POST 请求
    $.ajax({
        url: url,
        type: 'POST',
        data: jsonData, // 使用 JSON 字符串作为请求体
        processData: false, // 不处理数据
        contentType: 'application/json', // 明确设置内容类型为 JSON
        success: function(response){
            // 在这里处理上传成功后的操作
            showoff_class("dialog-wrapper change-password-dialog showup")
            showNotification('Success!');

        },
        error: function(xhr, status, error){
            console.error('上传失败:', error);
            // 在这里处理上传失败后的操作
        }
    });

});
