import { getUserNameAndAvatar
} from '/v1/diary-log/static/utils.js';

// $(function() {
//     navLoadAvatarAndSetUserName()
// });

export function navLoadAvatarAndSetUserName(){
    const getUserAvatarImageUrl = '/v1/diary-log/get-user-avatar-image'
    const avatarClass = ".user-info"
    const navInsertToDiv = "nav-fixed-child"

    var originAvatarDiv = document.getElementById(
        navInsertToDiv).querySelector(avatarClass);
    getUserNameAndAvatar(getUserAvatarImageUrl)
        .then(avatarUsernameDiv => {
        originAvatarDiv.innerHTML = avatarUsernameDiv.html()
        });

};

// function navLoadAvatarAndSetUserName(){
//     const avatarHtmlUrl = "/v1/diary-log/static/avatar.html"
//     const getUserAvatarImageUrl = '/v1/diary-log/get-user-avatar-image'
//     const avatarClass = ".user-info"
//     const navInsertToDiv = "nav-fixed-child"
//     // 使用fetch API获取数据
//     // fetch("/v1/diary-log/static/avatar.html")
//     fetch(avatarHtmlUrl)
//     .then(response => response.text()) // 解析响应为文本
//     .then(data => {
//         // debugger;
//         // 创建一个临时div来存放加载的HTML，以便查询特定元素
//         var tempDiv = document.createElement('div');
//         tempDiv.innerHTML = data;

//         // 提取并移除 <style> 元素
//         var styles = tempDiv.querySelectorAll('style');
//         Array.from(styles).forEach(style => {
//         document.head.insertAdjacentHTML('beforeend', `<style>${style.textContent}</style>`);
//         style.remove();
//         });

//         // debugger;
//         // 从加载的HTML中提取特定元素
//         // var specificElement = tempDiv.querySelector("#user-name-avatar");
//         var specificElement = tempDiv.querySelector(avatarClass);
//         // getUserAvatarImageUrl='/v1/diary-log/get-user-avatar-image'
//         getUserNameAndAvatar(getUserAvatarImageUrl)
//           .then(avatarUsernameDiv => {
//             specificElement.innerHTML = avatarUsernameDiv.html()
//             // 将特定元素添加到#account-info的最前面
//             // var accountInfo = document.querySelector("#nav-fixed-child");
//             var accountInfo = document.getElementById(navInsertToDiv);
//             if (accountInfo) {
//                 accountInfo.insertAdjacentElement('afterbegin', specificElement);
//             }
//           });

//     })
//     .catch(error => {
//         console.error('Error loading the HTML:', error);
//     });
// };