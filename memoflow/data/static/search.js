import { fetchData } 
    from '/v1/diary-log/static/utils.js';


export async function getSearchHtml() {
    const targetUrl = "/v1/diary-log/static/search.html";
    return fetchData(targetUrl)

     
    // // 同时开始两个请求
    // const [fetchedSourceUrlData, fetchedTargetUrlData] = await Promise.all([
    //     getNavSettingHtml(),
    //     fetchData(targetUrl)
    // ]);

    // const TargetDivClass = "SmHeadContent"

    // return addSourceDataToTargetDiv({
    //     sourceDivData: fetchedSourceUrlData, 
    //     targetDivData: fetchedTargetUrlData, TargetDivClass: TargetDivClass,
    //     placeFirst: true
    // })
    
};