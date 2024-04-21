import { fetchData, addSourceDataToTargetDiv } 
    from '/v1/diary-log/static/utils.js';

import { getSearchHtml,
} from '/v1/diary-log/static/search.js';

export async function getSmSearchDivHtml() {
    const targetUrl = "/v1/diary-log/static/sm_head_search.html";

    // 同时开始两个请求
    const [fetchedSourceUrlData, fetchedTargetUrlData] = await Promise.all([
        getSearchHtml(),
        fetchData(targetUrl)
    ]);

    const TargetDivClass = "SmSearchContent"

    return addSourceDataToTargetDiv({
        sourceDivData: fetchedSourceUrlData, 
        targetDivData: fetchedTargetUrlData, TargetDivClass: TargetDivClass,
        placeFirst: true
    })
};