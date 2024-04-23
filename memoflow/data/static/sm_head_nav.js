import { fetchData, addSourceDataToTargetDiv } 
    from '/v1/diary-log/static/utils.js';
import { navLoadAvatarAndSetUserName,
    getNavSettingHtml
} from '/v1/diary-log/static/setting/nav_setting.js';

export async function getSmHeadNavHtml() {
    const targetUrl = "/v1/diary-log/static/sm_head_nav.html";

     
    // 同时开始两个请求
    const [fetchedSourceUrlData, fetchedTargetUrlData] = await Promise.all([
        getNavSettingHtml(),
        fetchData(targetUrl)
    ]);

    const TargetDivClass = "SmHeadContent"

    return addSourceDataToTargetDiv({
        sourceDivData: fetchedSourceUrlData, 
        targetDivData: fetchedTargetUrlData, TargetDivClass: TargetDivClass,
        placeFirst: true
    })
};