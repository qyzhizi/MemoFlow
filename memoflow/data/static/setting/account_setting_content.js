import { set_user_name_and_avatar, checkElementExistence,
    getUserNameAndAvatar
} from '/v1/diary-log/static/utils.js';

// account-info
// 先使用AJAX获取数据
// $.get("/v1/diary-log/static/avatar.html", function(data) {
//     // 创建一个临时div来存放加载的HTML，以便查询特定元素
//     var tempDiv = $('<div>').html(data);

//     // 提取并移除 <style> 元素
//     var styles = tempDiv.find('style').text();
//     tempDiv.find('style').remove();
    
//     // 将 <style> 内容添加到当前文档的 <head> 中
//     $('head').append('<style>' + styles + '</style>');

//     // 从加载的HTML中提取特定元素
//     var specificElement = tempDiv.find("#user-name-avatar");

//     // 将特定元素添加到#content的最前面
//     $("#account-info").prepend(specificElement);
// });
export function loadAvatarAndSetUserName(url){
    // 使用fetch API获取数据
    // fetch("/v1/diary-log/static/avatar.html")
    fetch(url)
    .then(response => response.text()) // 解析响应为文本
    .then(data => {
        // debugger;
        // 创建一个临时div来存放加载的HTML，以便查询特定元素
        var tempDiv = document.createElement('div');
        tempDiv.innerHTML = data;

        // 提取并移除 <style> 元素
        var styles = tempDiv.querySelectorAll('style');
        Array.from(styles).forEach(style => {
        document.head.insertAdjacentHTML('beforeend', `<style>${style.textContent}</style>`);
        style.remove();
        });

        // debugger;
        // 从加载的HTML中提取特定元素
        // var specificElement = tempDiv.querySelector("#user-name-avatar");
        var specificElement = tempDiv.querySelector(".user-info");
        
        getUserNameAndAvatar(
          '/v1/diary-log/get-user-avatar-image')
          .then(avatarUsernameDiv => {
            specificElement.innerHTML = avatarUsernameDiv.html()
            // 将特定元素添加到#account-info的最前面
            var accountInfo = document.querySelector("#account-info");
            if (accountInfo) {
                accountInfo.insertAdjacentElement('afterbegin', specificElement);
            }
          });

    })
    .catch(error => {
        console.error('Error loading the HTML:', error);
    });
};



export function call_set_user_name_and_avatar(id){
    // debugger;
    set_user_name_and_avatar(id)
};




// 发送GET请求以获取配置信息并填充输入框
function getUserSyncFilesConfig() {
    $.ajax({
        url: '/v1/diary-log/get-user-sync-files',
        type: 'GET',
        success: function(response) {
            var jsonResponse = JSON.parse(response);
            // 请求成功处理
            $('#current-sync-filename-input').val(
                jsonResponse.current_sync_file);
            $('#other-syncfilename-input').val(
                jsonResponse.other_sync_file_list);
        },
        error: function(xhr, status, error) {
            // 请求失败处理
            console.error('Failed to get github config:', error);
        }
    });
}

// 调用函数以获取并填充配置信息
getUserSyncFilesConfig();    

function xhr_process_error(xhr, status, error) {
    // 读取失败时返回的内容
    // debugger;
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

$('#save-changes-button').click(function() {
    // 收集输入框的值
    // var gitRepPath = $('#gitRepPathInput').val();
    var CurrentSyncFileName = $('#current-sync-filename-input').val();
    var OtherSyncFilesName = $('#other-syncfilename-input').val();

    // 创建要发送的数据对象
    var data = {
        CurrentSyncFileName: CurrentSyncFileName,
        OtherSyncFilesName: OtherSyncFilesName
    };

    // 发送 POST 请求
    $.ajax({
        url: '/v1/diary-log/set-user-sync-files',
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
            }
            // debugger;
            if (jsonResponse.success === 1) {
                alert("Success");
            }
            else{alert("Failed, please check your configuration")}
            // 刷新页面
            getUserSyncFilesConfig();

        },
        error: xhr_process_error
    });

  
});

$('#pull_from_github').on('click', function(event) {
    event.preventDefault();
    // ask for confirmation
    if (!confirm("Are you sure to pull files from remote repo?")) {
        return;
    }
    $.ajax({
        url: '/v1/diary-log/sync-contents-from-repo-to-db',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        },
        success: function(response) {
            // console.log(response);
            // pop up a dialog
            alert(response);
            // reload the page
            // window.location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
    
            if (jqXHR.status === 401) {
                // 提示登录已过期
                alert("登录已过期，请重新登录");
                // HTTPUnauthorized error
                console.log("Unauthorized - Redirecting to login page");
                window.location.href = '/v1/diary-log/login';
            } else {
                // Handle other error types as needed
                console.log("Other error:", textStatus, errorThrown);
            }
        }
    });
});  

$('#edit-account-info').on('click', function(event) {
    // 使用fetch API获取数据
    fetch("/v1/diary-log/static/dialog-user-info.html")
    .then(response => response.text()) // 解析响应为文本
    .then(data => {
        // 获取 id 为 "dialog-wrapper-update-account" 的容器
        var container = document.getElementById('dialog-wrapper-update-account');
        let container_exsit = null;
        // 检查是否找到容器
        if (container !== null) {
            console.log('找到 id 为 "dialog-wrapper-update-account" 的容器。');
            container_exsit = true

        } else {
            container_exsit = false
            console.log('未找到 id 为 "dialog-wrapper-update-account" 的容器。');
        };

        if (!container_exsit) {
            // 在这里执行容器不存在时的逻辑
            // 创建一个临时div来存放加载的HTML，以便查询特定元素
            var tempDiv = document.createElement('div');
            tempDiv.innerHTML = data;

            // 提取并移除 <style> 元素
            var styles = tempDiv.querySelectorAll('style');
            Array.from(styles).forEach(style => {
                document.head.insertAdjacentHTML('beforeend',
                    `<style>${style.textContent}</style>`);
                style.remove();
            });

            // 从加载的HTML中提取特定元素
            // var specificElement = tempDiv.querySelector("#user-name-avatar");
            var specificElement = tempDiv.querySelector('div');

            // 创建一个新的 div 容器
            var containerDiv = document.createElement('div');
            // 将 specificElement 添加到新创建的 containerDiv 中
            containerDiv.appendChild(specificElement);
            // 将这个包含 specificElement 的 containerDiv 添加到 body 的最后
            document.body.appendChild(containerDiv);
        };
        // debugger;
        if (container_exsit){
            // debugger;
            $('.dialog-wrapper.update-account-dialog.showoff'
            ).removeClass('showoff').addClass('showup');

        };

        $('#remove-dialog-avatar').removeClass('showoff').addClass('showup');


        // 使用动态导入加载 account_setting_content.js 模块
        import('/v1/diary-log/static/dialog-user-info.js')
        .then(module => {
            // 模块加载成功
            // debugger;
            console.log('External account-setting-content.js loaded successfully');
            // module.set_user_avatar("#dialog-avatar")
            module.set_user_info_in_dialog(
                "dialog-username", "dialog-email", "dialog-avatar")
        
            // 这里可以添加你的事件监听器等其他 JavaScript 代码
            // 如果需要使用模块导出的函数或变量，可以通过 module.变量名 访问

        }).catch(err => {
            // 模块加载失败的错误处理
            console.error('Failed to load the module:', err);
        });


    })
    .catch(error => {
    console.error('Error loading the HTML:', error);
    });


});

// function checkElementExistence(element_id) {
//     // 获取 id 的容器
//     var container = document.getElementById(element_id);
//     let container_exist = null;
//     // 检查是否找到容器
//     if (container !== null) {
//         console.log('找到 id 为 "' + element_id + '" 的容器。');
//         container_exist = true;
//     } else {
//         container_exist = false;
//         console.log('未找到 id 为 "' + element_id + '" 的容器。');
//     };
//     return container_exist;
// };

function add_div_innerHTML_to_body(data){
    // 在这里执行容器不存在时的逻辑
    // 创建一个临时div来存放加载的HTML，以便查询特定元素
    var tempDiv = document.createElement('div');
    tempDiv.innerHTML = data;

    // 提取并移除 <style> 元素
    var styles = tempDiv.querySelectorAll('style');
    Array.from(styles).forEach(style => {
        document.head.insertAdjacentHTML('beforeend',
            `<style>${style.textContent}</style>`);
        style.remove();
    });

    // 从加载的HTML中提取特定元素
    // var specificElement = tempDiv.querySelector("#user-name-avatar");
    var specificElement = tempDiv.querySelector('div');

    // 创建一个新的 div 容器
    var containerDiv = document.createElement('div');
    // 将 specificElement 添加到新创建的 containerDiv 中
    containerDiv.appendChild(specificElement);
    // 将这个包含 specificElement 的 containerDiv 添加到 body 的最后
    document.body.appendChild(containerDiv);

};

function showup_class(class_name){
    class_name = '.' + class_name.split(' ').join('.');
    $(class_name).removeClass('showoff').addClass('showup');
};

function showoff_class(class_name){
    class_name = '.' + class_name.split(' ').join('.');
    $(class_name).removeClass('showup').addClass('showoff');
};

$('#edit-password').on('click', function(event) {
    // debugger;
    // 使用fetch API获取数据
    fetch("/v1/diary-log/static/dialog-user-password.html")
    .then(response => response.text()) // 解析响应为文本
    .then(data => {
        let container_id = 'dialog-wrapper-update-password'
        let container_exsit = checkElementExistence(container_id);
        if (!container_exsit) {
            add_div_innerHTML_to_body(data);
        };
        if (container_exsit){
            showup_class("dialog-wrapper change-password-dialog showoff")
        }
        
        // 使用动态导入加载 account_setting_content.js 模块
        import('/v1/diary-log/static/dialog-user-password.js')
        .then(module => {
            // 模块加载成功
            // debugger;
            console.log('External JavaScript dialog-user-password.js loaded successfully');
        
            // 这里可以添加你的事件监听器等其他 JavaScript 代码
            // 如果需要使用模块导出的函数或变量，可以通过 module.变量名 访问

        }).catch(err => {
            // 模块加载失败的错误处理
            console.error('Failed to load the module:', err);
        });

    })

});