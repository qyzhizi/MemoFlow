import { getUserNameAndAvatar,
    addSourceDataToTargetDiv,
    fetchData
} from '/v1/diary-log/static/utils.js';


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
