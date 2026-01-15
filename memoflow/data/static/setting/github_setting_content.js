// 获取链接元素的引用
  // 在此处设置断点
var link = document.getElementById('github-bind');

// 添加点击事件处理程序
link.addEventListener('click', function(event) {
    // 阻止默认的链接跳转行为
    event.preventDefault();

    // 在新页面中打开链接
    // window.open(link.href, '_blank');

    // 获取原窗口的宽度和高度
    var originalWidth = window.innerWidth;
    var originalHeight = window.innerHeight;

    // 子页面的宽度和高度设定为原窗口的一半
    var newWidth = originalWidth / 2;
    var newHeight = originalHeight / 2;

    // 计算新窗口的左上角位置，居中显示
    var leftPosition = (window.screen.width - newWidth) / 2;
    var topPosition = (window.screen.height - newHeight) / 2;

    // 在前面页面中打开子页面
    window.open(link.href, '_blank', 'width=' + newWidth + ',height=' + newHeight + ',left=' + leftPosition + ',top=' + topPosition);
});

// 发送GET请求以获取配置信息并填充输入框
function getGithubConfig() {
    $.ajax({
        url: '/v1/diary-log/get-github-config',
        type: 'GET',
        success: function(response) {
            var jsonResponse = JSON.parse(response);
            // 请求成功处理
            $('#gitRepPathInput').val(jsonResponse.gitRepPath);
        },
        error: xhr_process_error
    });
}

// 调用函数以获取并填充配置信息
getGithubConfig();    

function xhr_process_error(xhr, status, error) {
    // 读取失败时返回的内容
    var statusCode = xhr.status;
    var errorMessage = xhr.responseText;
            
    // 检查状态码是否为 4xx
    if (statusCode >= 400 && statusCode < 500) {
        // 如果返回的内容是 JSON 格式，可以尝试解析
        try {
            var errorData = JSON.parse(errorMessage);
            if ('VisibleError' in errorData) {
                alert('error: ' + errorData.VisibleError)}
        } catch (e) {
            console.error('Failed to parse error data:', e);
        }
    } else if(statusCode >= 500){
        // 如果返回的内容是 JSON 格式，可以尝试解析
        try {
            var errorData = JSON.parse(errorMessage);
            if ('VisibleError' in errorData) {
                alert('error: ' + errorData.VisibleError)}
        } catch (e) {
            console.error('Failed to parse error data:', e);
        }
    }
    else {
        console.log('Not a 4xx error, skipping parsing.');
    }
}

$('#github-save-changes-and-test-connection').click(function() {
    // 收集输入框的值
    var gitRepPath = $('#gitRepPathInput').val();

    // 创建要发送的数据对象
    var data = {
        gitRepPath: gitRepPath,
        // gitCurrentSyncFileName: gitCurrentSyncFileName,
        // gitOtherSyncFileName: gitOtherSyncFileName
    };

    // 发送 POST 请求
    $.ajax({
        url: '/v1/diary-log/github-config',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            var jsonResponse = JSON.parse(response);
            if (jsonResponse.success === 0) {
                if (jsonResponse.bad_credentials_exception) {
                    alert("Failed, 401 bad_credentials_exception, please check your configuration");
                }
                if (jsonResponse.unknown_object_exception){
                    alert("Failed, 404 unknown_object_exception, please check your configuration");
                }
            }
            else if (jsonResponse.success === 1) {
                alert("Success");
                // 刷新页面
                getGithubConfig();
            }
            else if (jsonResponse.config_input_flag === 0){
                alert("input `Git Repo Path` is empty")
            }
            else{alert("Failed, please check your configuration")}

        },
        error: xhr_process_error
    });

  
});
