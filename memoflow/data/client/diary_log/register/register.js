$(document).ready(function() {
    $('.register_form').submit(function(event) {
        event.preventDefault(); // 阻止默认的表单提交行为

        // 获取用户名和密码
        var username = $('input[type="text"]').val();
        var password = $('input[type="password"]').val();

        // 构造要发送的数据
        var data = {
            username: username,
            password: password
        };

        // 发送 POST 请求
        $.ajax({
            url: '/v1/diary-log/register',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                // 处理成功响应
                console.log(response);
                // 注册成功后跳转到登录页面
                window.location.href = '/v1/diary-log/login'; // 请根据实际情况修改登录页面的 URL
            },
            error: function(xhr, status, error) {
                // 处理错误响应
                console.error('There was a problem with your request:', error);
            }
        });
    });
});
