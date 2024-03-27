$(function() {

    // 获取链接元素的引用
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
        var newWindow = window.open(link.href, '_blank', 'width=' + newWidth + ',height=' + newHeight + ',left=' + leftPosition + ',top=' + topPosition);
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
                $('#gitCurrentSyncFileNameInput').val(jsonResponse.gitCurrentSyncFileName);
                $('#gitOtherSyncFileNameInput').val(jsonResponse.gitOtherSyncFileName);
            },
            error: function(xhr, status, error) {
                // 请求失败处理
                console.error('Failed to get github config:', error);
            }
        });
    }

    // 调用函数以获取并填充配置信息
    getGithubConfig();    

    $('#saveChangesButton').click(function() {
        // 收集输入框的值
        var gitRepPath = $('#gitRepPathInput').val();
        var gitCurrentSyncFileName = $('#gitCurrentSyncFileNameInput').val();
        var gitOtherSyncFileName = $('#gitOtherSyncFileNameInput').val();

        // 创建要发送的数据对象
        var data = {
            gitRepPath: gitRepPath,
            gitCurrentSyncFileName: gitCurrentSyncFileName,
            gitOtherSyncFileName: gitOtherSyncFileName
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
                        alert("401 bad_credentials_exception");
                    }
                    if (jsonResponse.unknown_object_exception){
                        alert("404 unknown_object_exception");
                    }
                    return;
                }
                if (jsonResponse.success === 1) {
                    alert("Success");
                }
                else{alert("Failed, please check your configuration")}
                // 请求成功处理
                console.log('Changes saved successfully.');
                // 刷新页面
                getGithubConfig();

            },
            error: function(xhr, status, error) {
                // 请求失败处理
                console.error('Failed to save changes:', error);
            }
        });
    });    
})