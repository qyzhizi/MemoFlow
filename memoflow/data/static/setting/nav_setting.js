import { getUserNameAndAvatar,
    addSourceDataToTargetDiv,
    fetchData
} from '/v1/diary-log/static/utils.js';


export function navLoadAvatarAndSetUserName(){
    const getUserAvatarImageUrl = '/v1/diary-log/get-user-avatar-image'
    const avatarClass = ".user-info"
    const navInsertToDiv = "nav-fixed-child"
    const navLogOut = "navLogOut"

    var originAvatarDiv = document.getElementById(
        navInsertToDiv).querySelector(avatarClass);
    getUserNameAndAvatar(getUserAvatarImageUrl)
        .then(avatarUsernameDiv => {
        originAvatarDiv.innerHTML = avatarUsernameDiv.html()
        });
    // 添加新的类名, 支持点击
    originAvatarDiv.classList.add('cursor-pointer');
    // 添加点击事件监听器
    originAvatarDiv.addEventListener('click', function() {
        var navLogOutDiv = document.getElementById(
            navLogOut);
        navLogOutDiv.classList.remove('!hidden')

    });
    var navLogOutDiv = document.getElementById('navLogOut');
    document.addEventListener('click', function(event) {
        // var navLogOutDiv = document.getElementById('navLogOut');
        var originAvatarDiv = document.getElementById(
            navInsertToDiv).querySelector(avatarClass);
    
        // 检查点击的元素是否是 navLogOutDiv 或其内部元素
        if (event.target !== navLogOutDiv && !navLogOutDiv.contains(event.target) &&
            event.target !== originAvatarDiv && !originAvatarDiv.contains(event.target)) {
            navLogOutDiv.classList.add('!hidden');
        }
    });

    navLogOutDiv.addEventListener('click', function(event){
        const logout_url = '/v1/diary-log/logout'
        $.ajax({
            url: logout_url,
            type: 'GET',
            success: function(response) {
                localStorage.removeItem('jwtToken');
                navLogOutDiv.classList.add('!hidden');
                window.location.href = '/v1/diary-log/login';

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error:", textStatus, errorThrown);
            }
        });


    });
    

};

export async function getNavSettingHtml() {
    const sourceUrl = "/v1/diary-log/static/avatar.html";
    const targetUrl = "/v1/diary-log/static/setting/nav_setting.html";

    // const fetchedSourceUrlData = await fetchData(sourceUrl);
    // const fetchedTargetUrlData = await fetchData(targetUrl);
    // 同时开始两个请求
    const [fetchedSourceUrlData, fetchedTargetUrlData] = await Promise.all([
        fetchData(sourceUrl),
        fetchData(targetUrl)
    ]);

     
    const idInTargetDiv = "nav-fixed-child"


    return addSourceDataToTargetDiv({
        sourceDivData: fetchedSourceUrlData, 
        targetDivData: fetchedTargetUrlData, idInTargetDiv: idInTargetDiv,
        placeFirst: true
    })
};
