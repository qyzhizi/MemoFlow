import { cropImage, Image2base64, 
    set_user_name_and_avatar, 
    showNotification } from '/v1/diary-log/static/utils.js';

function set_user_avatar(containerId){
    var url = '/v1/diary-log/get-user-avatar-image';
    // var containerId = "#dialog-avatar"
    $.ajax({
        url: url,
        type: 'GET',
        success: function(response) {
            // debugger;
            if (typeof response === 'string') {
                // 如果response是字符串，尝试解析它
                try {
                    response = JSON.parse(response);
                } catch (e) {
                    console.error("解析错误", e);
                }
            } 
            var username = response.username;
            var base64Data = response.avatar_image;
            // 使用jQuery选择器获取div元素
            // var $div = $('body').find('#' + containerId);
            // let $div = $(containerId);
            let $div = $('body').find(containerId);

            if (response.avatar_image) {
                // 创建新的img元素并设置其属性
                let $newImg = $('<img>').attr({
                    // src: 'data:image/png;base64,' + base64Data,
                    src: base64Data,
                    decoding:"async",
                    loading: "lazy",
                    alt: 'Avatar'
                });
                 // 清空div的当前内容并添加新的img和span元素
                $div.empty().append($newImg);

            } else {
                let $newImg = $('<img>').attr({
                    src: "https://via.placeholder.com/150",
                    alt:"Avatar"
                    });
                 // 清空div的当前内容并添加新的img和span元素
                $div.empty().append($newImg);
            }
            // // 清空div的当前内容并添加新的img和span元素
            // $div.empty().append($newImg);
        }
    });
};


async function set_user_info_in_dialog(
    dialog_username_id,
    dialog_email_id,
    dialog_avatar_container_id
    ){
    var url = '/v1/diary-log/get-user-account-info';
    // var containerId = "#dialog-avatar"
    // 使用 await 等待异步操作完成
    try {
        let response = await $.ajax({
            url: url,
            type: 'GET'
        });
        // debugger;
        if (typeof response === 'string') {
            // 如果response是字符串，尝试解析它
            try {
                response = JSON.parse(response);
            } catch (e) {
                console.error("解析错误", e);
            }
        } 
        var username = response.username;
        var base64Data = response.avatar_image;
        var email = response.email;

        $('#' + dialog_username_id).val(username);
        $('#' + dialog_email_id).val(email);


        let $div = $('body').find('#' + dialog_avatar_container_id);

        if (response.avatar_image) {
            // 创建新的img元素并设置其属性
            let $newImg = $('<img>').attr({
                // src: 'data:image/png;base64,' + base64Data,
                src: base64Data,
                decoding:"async",
                loading: "lazy",
                alt: 'Avatar'
            });
             // 清空div的当前内容并添加新的img和span元素
            $div.empty().append($newImg);

        } else {
            let $newImg = $('<img>').attr({
                src: "https://via.placeholder.com/150",
                alt:"Avatar"
                });
             // 清空div的当前内容并添加新的img和span元素
            $div.empty().append($newImg);
        }
        
        
    } catch (error) {
        console.error("请求失败", error);
        throw error; // 抛出异常，以便调用者可以捕获
    }

};

function dialog_wrapper_showoff(){
    $('.dialog-wrapper.update-account-dialog.showup'
        ).removeClass('showup').addClass('showoff');
};

function remove_dialog_avatar_flag_showoff(){
    $('#remove-dialog-avatar').removeClass('showup'
        ).addClass('showoff');
};

function remove_dialog_avatar_flag_showup(){
    $('#remove-dialog-avatar').removeClass('showoff'
        ).addClass('showup');
};

// $(function() {
//     debugger;
    
var display_id = 'dialog-avatar';
$('body').on('change', '#dialog-avatar-input', 
    function(evt) {
        // debugger;
        // var display_id = 'dialog-avatar';
        cropImage(evt).then(function(newImg) {
            // 在这里可以使用处理后的图片 newImg
            $('#' + display_id).empty().append(newImg);
            remove_dialog_avatar_flag_showup()
            // $('body').find('#' + display_id).empty().append(newImg);
        }).catch(function(error) {
            // 如果发生错误，可以在这里处理
            console.error(error);
        });
});

$('body').on('click', '#cancel-account-info-edit, #close-account-info-edit', 
    function() {
        dialog_wrapper_showoff()
});

$('body').on('click', '#remove-dialog-avatar', 
    function() {
        // debugger;
        let $div = $('body').find('#' + display_id);
        let $newImg = $('<img>').attr({
            src: "https://via.placeholder.com/150",
            alt:"Avatar"
            });
        $div.empty().append($newImg);

        remove_dialog_avatar_flag_showoff()
});


$('body').on('click', '#save-account-info-edit', function() {
    var url = '/v1/diary-log/set-user-account-info';
    var dialog_avatar_id = '#' + 'dialog-avatar';
    // debugger;
    // 获取具有特定 id 的输入元素
    var avatar_src_value = '';
    // 查找 id 为 "dialog-avatar" 的元素下的第一个 <img> 元素
    var imgElement = $(dialog_avatar_id +" img:first");
    // 检查是否找到了 <img> 元素
    if (imgElement.length > 0) {
        // 如果找到了，则获取其 src 属性内容并输出到控制台
        var avatar_src_value = imgElement.attr("src");
        // console.log(avatar_src_value);
    } else {
        // 如果没有找到 <img> 元素，则输出相应的提示信息到控制台
        console.log("在 id 为 'dialog-avatar' 的元素中找不到 <img> 元素。");
    }

    // let fileInput = document.getElementById('dialog-avatar-input')
    var username_value = document.getElementById('dialog-username').value;
    var email_value = document.getElementById('dialog-email').value;
    if (username_value === '') {
        alert('请填写用户名！');
        return;
    }


    // 假设 fileInput, username_value, email_value 已经定义
    // Image2base64(fileInput.files[0]).then((base64) => {
        // 创建一个普通的 JavaScript 对象来存储数据
    let data; // Declare `data` outside the if-else scope to ensure it is accessible later.

    data = {
        image: avatar_src_value,
        username: username_value,
        email: email_value
    };

    // Convert the object to a JSON string
    let jsonData = JSON.stringify(data);


    // 发送 POST 请求
    $.ajax({
        url: url,
        type: 'POST',
        data: jsonData, // 使用 JSON 字符串作为请求体
        processData: false, // 不处理数据
        contentType: 'application/json', // 明确设置内容类型为 JSON
        success: function(response){
            console.log('上传成功');
            // 在这里处理上传成功后的操作
            dialog_wrapper_showoff()
            set_user_name_and_avatar('#user-name-avatar')
            // .then(() => alert('Success!'))
            .then(() => showNotification('Success!'))
            .catch(error => console.error("操作失败", error));

        },
        error: function(xhr, status, error){
            console.error('上传失败:', error);
            // 在这里处理上传失败后的操作
        }
    });


    //     // 这里可以进行其他需要在base64转换完成后执行的操作
    // }).catch((error) => {
    //     // 处理转换错误
    //     console.error('转换为base64时出错：', error);
    //     });

    
});

// $('body').on('click', '#save-account-info-edit', function() {

// });

export { set_user_avatar, set_user_info_in_dialog };