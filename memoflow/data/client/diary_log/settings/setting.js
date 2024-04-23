import { addDivInnerHTMLToBodyContainer, checkElementExistence,
    addSourceDataToTargetDiv, fetchData } 
    from '/v1/diary-log/static/utils.js';
import { navLoadAvatarAndSetUserName,
    getNavSettingHtml
} from '/v1/diary-log/static/setting/nav_setting.js';


$(function() {
    //导入导航栏
    getNavSettingHtml()
    .then(html => {
        addDivInnerHTMLToBodyContainer(
            {doc_data: html, container_id: 'nav-container-root' })
        
        navLoadAvatarAndSetUserName('nav-container-root')
    })
    .catch(error => {
        console.error(error); // 错误处理
    });

    // 使用 $() 函数获取元素
    var MainSettingContentContainer = $('#main-setting-content');

    // 添加容器的函数
    function switchContainer(containerId) {

        // 隐藏 MainSettingContentContainer 内容的元素
        MainSettingContentContainer.children().hide();

        // 检查是否已经包含容器
        if (MainSettingContentContainer.find('#' + containerId).length) {
            $("#" + containerId).show().siblings(".setting-content").hide();
            return; // 不执行后续步骤
        }
    
        // 创建 XMLHttpRequest 对象
        var xhr = new XMLHttpRequest();
        if (containerId === 'github-setting-content') {
            // 配置请求
            xhr.open('GET', 
            '/v1/diary-log/static/setting/github_setting_content.html', true);
        } else if(containerId === 'jianguoyun-setting-content') {
            xhr.open('GET', 
            '/v1/diary-log/static/setting/jianguoyun_setting_content.html', true);
        } else if(containerId === 'account-setting-content') {
            xhr.open('GET', 
            '/v1/diary-log/static/setting/account_setting_content.html', true);
        }
    
        // 定义请求完成时的处理函数
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                // 创建一个虚拟的 div 元素
                var tempDiv = document.createElement('div');
                // 将请求返回的内容填充到虚拟的 div 元素中
                tempDiv.innerHTML = xhr.responseText;
    
                // 获取容器元素
                var container = tempDiv.querySelector('#' + containerId);
                // 如果容器存在，则将其添加到主容器中
                if (container) {

                    MainSettingContentContainer.append(container.cloneNode(true));

                    $("#" + containerId).show().siblings(
                        ".setting-content").hide();

                    if (containerId === 'github-setting-content') {
                        // 加载并执行外部 JavaScript 文件
                        $.getScript(
                            "/v1/diary-log/static/setting/github_setting_content.js",
                        function() {
                            // JavaScript 文件加载完成后执行的操作
                            console.log(
                                'External JavaScript github_setting_content.js  loaded successfully');
                            // 这里可以添加你的事件监听器等其他 JavaScript 代码
                        });
                    } else if (containerId === 'jianguoyun-setting-content'){
                        // 加载并执行外部 JavaScript 文件
                        $.getScript(
                            "/v1/diary-log/static/setting/jianguoyun_setting_content.js",
                        function() {
                            // JavaScript 文件加载完成后执行的操作
                            console.log(
                                'External JavaScript jianguoyun_setting_content.js loaded successfully');
                            // 这里可以添加你的事件监听器等其他 JavaScript 代码
                        });
                    } else if (containerId === 'account-setting-content'){

                        // 使用动态导入加载 account_setting_content.js 模块
                        import('/v1/diary-log/static/setting/account_setting_content.js')
                        .then(module => {
                            // 模块加载成功
                            console.log('External JavaScript account-setting-content.js loaded successfully');
                             
                            module.loadAvatarAndSetUserName('/v1/diary-log/static/avatar.html')
                            
                            // 这里可以添加你的事件监听器等其他 JavaScript 代码
                            // 如果需要使用模块导出的函数或变量，可以通过 module.变量名 访问

                        }).catch(err => {
                            // 模块加载失败的错误处理
                            console.error('Failed to load the module:', err);
                        });

                    }
                } else {
                    console.error('Container not found:', containerId);
                }
            } else {
                console.error('Request failed:', xhr.status);
            }
        };
        // 发送请求
        xhr.send();
    }
    
    // 默认显示第一个容器，并隐藏其他容器
    switchContainer("account-setting-content")
    
    // github setting content listener click
    $('.nav-setting-opt').on('click', function(event) {

        // 获取对应的容器元素的id
        var targetId = $(this).data("target");

        switchContainer(targetId);
    
        // 隐藏其他容器元素，显示对应的容器元素
        // $("#" + targetId).show().siblings(".setting-content").hide();
    });

})
