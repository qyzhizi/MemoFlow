import { addDivInnerHTMLToBodyContainer } 
    from '/v1/diary-log/static/utils.js';
import { navLoadAvatarAndSetUserName,
    getNavSettingHtml
} from '/v1/diary-log/static/setting/nav_setting.js';
import {  getSmHeadNavHtml
} from '/v1/diary-log/static/sm_head_nav.js';
import {  getSmSearchDivHtml
} from '/v1/diary-log/static/sm_head_search.js';
import {
    showNotification
} from '/v1/diary-log/static/utils.js';

if (function() { return !this; }()) {
    console.log("严格模式下运行");
} else {
    console.log("非严格模式下运行");
}


$(function() {
    window.onload = adjustLayout;
    window.onresize = adjustLayout;

    const log_textarea = document.getElementById('log');
    const edit_textarea = document.getElementById('editLog');
    // 绑定 input 事件监听器，以便在输入时调整高度
    // log_textarea.addEventListener('input', autoResize);
    log_textarea.addEventListener('input', function(event) {
        autoResize('log');
    });
    // edit_textarea.addEventListener('input', autoResize);
    edit_textarea.addEventListener('input', function(event) {
        autoResize('editLog');
    });
    autoResize('log')
    // autoResize('editLog')

    localStorage.setItem('page_size', null);
    localStorage.setItem('page_number', null);
    // get logs
    getLogs()
     
    //导入导航栏
    getNavSettingHtml()
    .then(html => {
        addDivInnerHTMLToBodyContainer(
            {doc_data: html, container_id: 'nav-container-root' })
        
        // // 添加新的类名
        // var userInfoDiv = document.getElementById('nav-container-root').querySelector('.user-info')
        // userInfoDiv.classList.add('cursor-pointer');

        navLoadAvatarAndSetUserName('nav-container-root')
    })
    .catch(error => {
        console.error(error); // 错误处理
    });



    $('#submit').on('click', function(event) {
        event.preventDefault();
        addLog()
    });

    // search-input
    inputSearchHandler(document.getElementById('search-input'))
    showSmHeadNavHandler()
    // show sm-width search sidebar
    showSmHeadSearchAndTagsHandler()


    $('#click-more-log').on('click', function(event) {
        event.preventDefault();
        // 从 localStorage 中读取 page_size 和 page_number
        // 如果不存在则使用默认值 10
        var page_size =  localStorage.getItem('page_size'); 
        // 如果不存在则使用默认值 1
        var page_number = localStorage.getItem('page_number') || 1; 
        page_number = (parseInt(page_number) + 1).toString()
        getLogs(page_size=page_size, page_number=page_number)
    })


    var txtInput = document.getElementById('log');
    txtInput.addEventListener('keydown', alt_q);
    txtInput.addEventListener('keydown', tab_to_space);

    var editTxtInput = document.getElementById('editLog');
    editTxtInput.addEventListener('keydown', alt_q);
    editTxtInput.addEventListener('keydown', tab_to_space);

    // 监听窗口关闭事件
    window.addEventListener("beforeunload", function (event) {
        var inputBox = document.getElementById("log");
                // 检测输入框内容是否为空
        if (inputBox.value.trim().length > 0) {
            // 显示提示框
            event.preventDefault();
            // beforeunload 事件的返回值
            event.returnValue = " ";
        }
    });
    // 监听窗口关闭事件，当编辑窗口未关闭时给出提示
    window.addEventListener("beforeunload", function (event) {
        // 获取编辑框元素
        var modal = document.getElementById('editLogModal');
        // 检测编辑框是否为打开状态
        if (modal.style.display === "flex") {
            // 显示提示框
            event.preventDefault();
            // beforeunload 事件的返回值
            event.returnValue = " ";
        }
    });
    // copyIconSvgButtonListener();

});

function adjustLayout() {
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.documentElement.style.setProperty('--scrollbar-width', `${scrollbarWidth}px`);
}
  
// 定义一个防抖函数
function debounce(func, delay) {
    let timeoutId;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(context, args);
        }, delay);
    };
}

function inputSearchHandler(inputElement) {
    // const inputElement = document.getElementById('search-input');
    // const inputElement = document.getElementById(inputSearchID);

    // 定义一个处理输入事件的函数
    const handleInput = debounce(function() {
        const inputValue = inputElement.value.trim(); // 获取输入值并去除首尾空格

        if (inputValue) {
            // 如果有输入值，则发送请求
            console.log("发送请求，搜索关键词为:", inputValue);

            // 示例：发送GET请求
            // 注意：这里的URL需要替换成你的实际请求URL
            // 同时，这里的请求仅为示例，具体实现可能需要根据实际API进行调整
            fetch('/v1/diary-log/list-log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(
                    { filters: {content : '%' + inputValue + '%'} }),
            })
                .then(response => response.json())
                .then(data => {
                    // console.log("请求结果:", data);
                    // 处理请求结果
                    
                    var clickMoreLog = document.getElementById("click-more-log");
                    clickMoreLog.classList.add('!hidden');
                    document.getElementById("logList").innerHTML = "";
                    for (var i = 0; i < data.logs.length; i++) {
                        addLogEntry(data.logs[i], data.ids[i], false);
                    }
                })
                .catch(error => {
                    console.error("请求失败:", error);
                });
        }
    }, 1000); // 延迟1000毫秒

    // 监听输入事件，并应用防抖处理
    inputElement.addEventListener('input', handleInput);
}


function showSmHeadNavHandler() {
    $('#SmHeadNavButton').on('click', function(event) {
        event.preventDefault();
        var SmHead = document.getElementById('SmHeadRoot').querySelector(".SmHead");

        if (SmHead) {
            console.log("SmHead 存在");
            SmHead.classList.remove('!hidden')
        } else {
            console.log("SmHead 不存在");
            getSmHeadNavHtml()
                .then(html => {
                    addDivInnerHTMLToBodyContainer({
                        doc_data: html,
                        container_id: 'SmHeadRoot'
                    });

                    navLoadAvatarAndSetUserName('SmHeadRoot')
                    var SmHead = document.getElementById('SmHeadRoot').querySelector(".SmHead");
                    // 监听 SmHead 的点击事件
                    SmHead.addEventListener('click', function(event) {
                        // 检查点击是否在 nav-fixed-child 或其子元素上
                        var clickedElement = event.target;
                        var navFixedChild = SmHead.querySelector('.nav-fixed-child');

                        // 如果 navFixedChild 存在并且点击的不是 nav-fixed-child 或其子元素
                        if (navFixedChild && !navFixedChild.contains(clickedElement)) {
                            // 隐藏 SmHead
                            SmHead.classList.add('!hidden');
                        }
                    });

                })
                .catch(error => {
                    console.error(error); // 错误处理
                });
        }
    });
}

function showSmHeadSearchAndTagsHandler() {
    $('#SmHedadSearchButton').on('click', function(event) {
        event.preventDefault();
        let smSerchSidebarModule = document.getElementById(
            'SmSearchRoot').querySelector(".smSerchSidebarModule");

        if (smSerchSidebarModule) {
            console.log("smSerchSidebarModule 存在");
            smSerchSidebarModule.classList.remove('!hidden')
        } else {
            console.log("smSerchSidebarModule 不存在");
            getSmSearchDivHtml()
                .then(html => {
                    addDivInnerHTMLToBodyContainer({
                        doc_data: html,
                        container_id: 'SmSearchRoot'
                    });

                    let smSerchSidebarModule = document.getElementById(
                        'SmSearchRoot').querySelector(".smSerchSidebarModule");
                    // 监听 SmHead 的点击事件
                    smSerchSidebarModule.addEventListener(
                        'click', function(event) {
                        // 检查点击是否在 SmSearchContent 或其子元素上
                        var clickedElement = event.target;
                        var SmSearchContent = smSerchSidebarModule.querySelector('.SmSearchContent');

                        // 如果 SmSearchContent 存在并且点击的不是 SmSearchContent 或其子元素
                        if (SmSearchContent && !SmSearchContent.contains(clickedElement)) {
                            // 隐藏 SmHead
                            smSerchSidebarModule.classList.add('!hidden');
                        }
                    });
                    // 监听 smSearchInput 搜索事件
                    inputSearchHandler(document.getElementById(
                        'SmSearchRoot').querySelector(".smSearchInput"))

                })
                .catch(error => {
                    console.error(error); // 错误处理
                });
        }
    });
}


function autoResize(textarea_id) {
    //  
    const textarea = document.getElementById(textarea_id);
    // 设置高度为 auto，以获取正确的 scrollHeight
    textarea.style.height = 'auto';
    // 设置高度为 scrollHeight，可能需要加上边框的高度（如果有的话）
    textarea.style.height = `${textarea.scrollHeight}px`;
}



function addLogEntry(logText, record_id, reverse=true) {
    var log_entry = $('<div class="log_entry"></div>'); // 添加一个类以便样式控制
    // 将 log_entry 元素的内容添加到 log_entry 中
    log_entry.text(logText);
    log_entry.data('logText', logText);
    processLogEntryText(log_entry);
    // 创建一个包含下拉菜单的容器
    var logEntryContainer = $('<div class="log-entry-container"></div>');
    // 下拉菜单图标容器
    var dropdownContainer = $('<div class="dropdown-container"></div>');
    // 下拉菜单图标
    var dropdownIcon = $(
        '<span class="btn more-action-btn">' +
        '   <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-more-vertical icon-img">' +
        '       <circle cx="12" cy="12" r="1"></circle>' +
        '       <circle cx="12" cy="5" r="1"></circle>' +
        '       <circle cx="12" cy="19" r="1"></circle>' +
        '   </svg>' +
        '</span>'
    );
    // 下拉菜单
    var dropdownMenu = $('<div class="dropdown-menu"></div>');

    // 将 record_id 添加到 dropdownMenu 作为属性
    dropdownMenu.data('record_id', record_id);
    // dropdownMenu.attr('record_id', record_id);

    // 添加复制选项
    var copyOption = $('<div class="dropdown-option copy-option">复制</div>');
    // 添加编辑选项
    var editOption = $('<div class="dropdown-option edit-option">编辑</div>');
    // 添加删除选项
    var deleteOption = $('<div class="dropdown-option delete-option">删除</div>');
    // 添加LatexView选项
    // var latexView = $('<div class="dropdown-option latexView-option">latexView</div>');

    // 将下拉菜单图标添加到 dropdownContainer 中
    dropdownContainer.append(dropdownIcon);
    // 将下拉菜单添加到 dropdownContainer 中
    dropdownContainer.append(dropdownMenu);
    // 将 dropdownContainer 添加到 logEntryContainer 中
    logEntryContainer.append(dropdownContainer);
    // 将 log_entry 添加到 logEntryContainer 中
    logEntryContainer.append(log_entry);
    // 将 logEntryContainer 添加到 logList 中
    var logList= $('#logList');
    if(reverse == true){
        logList.prepend(logEntryContainer);
    } else{
        logList.append(logEntryContainer);
    }

    // 点击下拉菜单图标时触发事件
    dropdownIcon.click(function(event) {
        // 阻止事件冒泡
        event.stopPropagation();
        // 显示或隐藏下拉菜单
        dropdownMenu.toggle();
    });

    // 在文档的其他位置点击时隐藏下拉菜单
    $(document).click(function() {
        dropdownMenu.hide();
    });

    // 添加复制选项点击事件处理程序
    // copyOption.click(function() {
    //     // 复制日志文本到剪贴板
    //     // copyToClipboard(removeLogseqMatches(pre.text()));
    //     copyToClipboard(removeLogseqMatches(
    //         log_entry.data('logText')));
    //     // 隐藏下拉菜单
    //     dropdownMenu.hide()
    // });
    // 获取 copyOption 元素对应的 DOM 元素
    let copyOptionDOM = copyOption.get(0);
    let clipboard = new ClipboardJS(copyOptionDOM, {
        text: function(trigger) {
          return removeLogseqMatches(
            log_entry.data('logText'));
        }
      });
    // 处理复制成功事件（可选）
    clipboard.on('success', function(e) {
        console.log('复制成功');
        showNotification('Copy Success!', 700);
        e.clearSelection();
    });
    
    // 处理复制失败事件（可选）
    clipboard.on('error', function(e) {
        console.error('复制失败：', e.action);
    });

    // 添加编辑选项点击事件处理程序
    editOption.click(function() {
        record_id = dropdownMenu.data('record_id')
        console.log("record_id : ", record_id)
        // 编辑日志条目
        editLogEntry(log_entry, record_id);
        // 隐藏下拉菜单
        dropdownMenu.hide();
    });

    // 添加删除选项点击事件处理程序
    deleteOption.click(function() {
        record_id = dropdownMenu.data('record_id')
        console.log("record_id : ", record_id)
        // 弹窗提示，是否删除
        if (confirm('确定要删除该条日志吗？')) {
            // 删除日志条目
            deleteLogEntry(record_id, logEntryContainer);
            // 隐藏下拉菜单
            dropdownMenu.hide();
        }
    });

    // latexView 选项点击事件处理程序
    // latexView.click(function() {
    //     // 渲染当前笔记中出现的公式
    //     renderLatexInLog(log_entry);
        
    //     // renderLatexInLog 这里 重置了 html, 需要重新设置监听函数
    //     // 获取替换后的代码块元素
    //     var codeContainers = log_entry.find('.code-container');
    //     // 为每个代码块元素添加点击事件监听器
    //     codeContainers.each(function() {
    //         var button = $(this).find('.copyIconSvgButton');
    //         copyIconSvgButtonListener(button);
    //     });
    //     // 隐藏下拉菜单
    //     dropdownMenu.hide();
    // });


    // 将复制、编辑和删除选项添加到下拉菜单中
    dropdownMenu.append(copyOption);
    dropdownMenu.append(editOption);
    dropdownMenu.append(deleteOption);
    // dropdownMenu.append(latexView);
}


/**
* 将字符串根据给定的模式分割，并返回匹配项和分隔符的列表
* @param {string} inputString - 要分割的字符串
* @param {RegExp} pattern_t - 用于分割字符串,带有 g (global) 标志的正则表达式
* @returns {string[]} - 包含匹配项和分隔符的列表
*/
function splitStringWithPattern(inputString, pattern_t) {
    // 检查 pattern_t 是否是带有全局标志的正则表达式
    if (!pattern_t.global) {
    console.error("Error: pattern_t must have the global (g) flag.");
    return;
    }
    let match;
    let match_list = [];
    let old_index = 0;
    
    while ((match = pattern_t.exec(inputString)) !== null) {
        match_list.push(inputString.substring(old_index, match.index));
        match_list.push(match[0]);
        // pattern_t.lastIndex 用于记录正则表达式匹配的最后一个字符的位置
        // 这要求pattern_t 是带有 g (global) 标志的正则表达式，否则一直是 0
        old_index = pattern_t.lastIndex;
    }
    if (old_index != 0){
        match_list.push(inputString.substring(old_index));}
    return match_list;
}


/**
 * 对给定的 process_input 数组进行处理，根据匹配项进行相应操作，并返回处理后的字符串。
 * @param {Array} process_input 包含待处理数据的数组。
 * @param {RegExp} pattern_logseq_child - 用于分割字符串的正则表达式模式
 * @returns {String} 处理后的字符串。
 */
function processInputAndReturnString(process_input, pattern_logseq_child) {
    // 遍历 process_input 数组，只输出 匹配项
    for (let i = 1; i < process_input.length; i += 2) {
        let index = i
        let strings_index = i +1
        let pattern_logseq = process_input[i]
        let child_string = process_input[strings_index]
        // 将pattern_logseq 按 “-” 分割
        pattern_logseq = pattern_logseq.split("-")
        let num_t_logseq = pattern_logseq[0].length

        let child_block_list;
        child_block_list = splitStringWithPattern(child_string, pattern_logseq_child)
        for (let i = 1; i < child_block_list.length; i += 2) {
            if (child_block_list[i].split(' ')[0].length < num_t_logseq){
                child_block_list[i+1] = "@ans " + child_block_list[i+1]
                var combinedString = child_block_list.join(""); // 使用空串作为分隔符
                process_input[strings_index] = combinedString;
                break
            }
        }
    }    
    return process_input.join("");
}


// Cancel Logseq format
function removeLogseqMatches(inputString) {
    var pattern_logseq_mian = /^[\x20]{0,}\t{0,}-[\x20]/gm
    var pattern_logseq_child = /^[\x20]{0,}\t{0,}[\x20]{2}/gm;
    var result1 = splitStringWithPattern(inputString, pattern_logseq_mian);
    if ( result1 && result1.length === 0){
        return inputString
    }
    inputString = processInputAndReturnString(result1, pattern_logseq_child)

    // 匹配行首的 "  " "\t  " "\t\t  " "\t\t\t  " 等等, 替换为空串
    // ^[\x20]{2} ：表示行首两个空格，匹配 `#ans` 之前的行
    const pattern = /^[\x20]{0,}\t{1,}[\x20]{2}|^[\x20]{2}/gm;
    const String1 = inputString.replace(pattern, '')

    // 使用正则表达式进行划分
    var regex = /^\t-[\x20]#ans/gm;
    const pattern_t = /^\t- #/gm;
    var splittedParts = [];
    // 检查 regex 是否是带有全局标志的正则表达式
    if (!regex.global) {
    console.error("Error: #ans regex must have the global (g) flag.");
    return;
    }
    var match = regex.exec(String1); // 使用 exec 方法进行匹配
    if (match) {
        var index = match.index;
        var firstPart = String1.substring(0, index); // 第一个部分是匹配之前的字符串
        var secondPart = String1.substring(regex.lastIndex); // 第二个部分是匹配之后的字符串
        splittedParts.push(firstPart, secondPart);
    } else {
        splittedParts.push(String1); // 如果没有匹配到，直接将整个字符串加入列表
    }
    // 如果长度为 1，说明字符串中没有包含 #ans
    if (splittedParts.length === 1) {
        const pattern1_0 = /^[\x20]{0,}\t-[\x20]/gm;
        let result = splittedParts[0].replace(pattern_t, '#');
        result = result.replace(pattern1_0, '- ');
        console.log("输入字符串中没有包含 #ans");
        return result.substring(2);
    }
    // 如果长度等于 2，说明字符串中包含了 #ans
    if (splittedParts.length == 2) {
        console.log("输入字符串中包含了 #ans");
        splittedParts[0] = splittedParts[0].replace(pattern_t, '#');

        var part1 = splittedParts[0];
        var part2 = splittedParts[1];
        const pattern1_0 = /^[\x20]{0,}\t-[\x20]/gm;
        part1 = part1.replace(pattern1_0, '- ');
        const pattern2_0 = /^[\x20]{0,}\t-[\x20]/gm;
        const pattern2_1 = /^[\x20]{0,}\t\t-[\x20]/gm;
        const pattern2_2 = /^[\x20]{0,}\t\t\t-[\x20]/gm;
        part2 = part2.replace(pattern2_0, '@blk ');
        part2 = part2.replace(pattern2_1, '- ');
        part2 = part2.replace(pattern2_2, '@blk- ');
        var result = part1 +"#ans"+ part2;
        return result.substring(2);
    }
}

// 复制到剪贴板函数
// function copyToClipboard(text) {
//     // 创建一个新的 ClipboardItem 对象
//     const clipboardItem = new ClipboardItem({ "text/plain": new Blob([text], { type: "text/plain" }) });
  
//     // 将文本添加到剪贴板
//     navigator.clipboard.write([clipboardItem]).then(function() {
//       console.log('文本已成功复制到剪贴板');
//     }).catch(function(err) {
//       console.error('复制失败:', err);
//     });
//   }

// function copyToClipboard(text) {
//     var tempInput = document.createElement("input");
//     tempInput.value = text;
//     document.body.appendChild(tempInput);
//     tempInput.select();
//     document.execCommand("copy");
//     document.body.removeChild(tempInput);
// }


// let modalMousedownisListenerAttached = false;
var modal = document.getElementById('editLogModal');
var modalContent = modal.querySelector('.modal-content');
var isModalMouseDown = false;

function modalMousedownAttachListener(modal, modalContent) {
    // if (!modalMousedownisListenerAttached) {
        modal.addEventListener('mousedown', function(event) {
            if (!modalContent.contains(event.target)) {
                console.log("isMouseDown = true;");
                isModalMouseDown = true;
            }
            event.stopPropagation(); // 阻止事件冒泡
        });
        // modalMousedownisListenerAttached = true;
    // }
}
modalMousedownAttachListener(modal, modalContent);

    
modal.addEventListener('mouseup', function(event) {
    console.log("enter addEventListener modal mouseup ")
    if (!modalContent.contains(event.target) && isModalMouseDown) {
        event.preventDefault(); // 阻止默认的操作
        //  
        var confirmation = confirm("是否关闭编辑页面？");
        console.log("关闭编辑页面？")

        // 如果用户点击确定按钮
        if (confirmation) {
            // 清空编辑框
            editLog.value = '';
            editLog.curPreObject = null;
            editLog.cur_record_id = null;
            // 关闭模态框
            modal.style.display = "none";
        } else {
            // 如果用户点击取消按钮，则什么也不做
            // 用户选择不保存，取消关闭操作
        }
    }
    isModalMouseDown = false;
});  



// 获取关闭按钮，并为其添加点击事件处理程序
var closeBtn = document.getElementsByClassName("close")[0];
closeBtn.onclick = function() {
    var editLog = document.getElementById('editLog');
    // 弹出窗口提示是否提交
    var confirmation = confirm("是否关闭编辑页面？");

    // 如果用户点击确定按钮
    if (confirmation) {
        // 清空编辑框
        editLog.value = '';
        editLog.curPreObject = null;
        editLog.cur_record_id = null;
        // 关闭模态框
        modal.style.display = "none";
    } 

}


// 获取保存按钮
var saveChangesBtn = document.getElementById('saveChangesBtn');
// 当用户点击保存按钮时
saveChangesBtn.onclick = function() {
    var modal = document.getElementById('editLogModal');
    // 获取编辑框中的文本域
    var editLog = document.getElementById('editLog');

    // 获取cur_record_id属性的值
    var curRecordId = editLog.getAttribute('cur_record_id');
    var log_entry = editLog.curPreObject;
    // 获取编辑后的日志内容
    var editedText = editLog.value;

    // 这里可以发送请求到后端，保存编辑后的日志内容
    if (editedText === '') {
        console.log("log is none")
        return; // 退出函数
    }

    $.ajax({
        url: '/v1/diary-log/updatelog',
        type: 'POST',
        // headers: {
        //     'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        // },
        contentType: 'application/json',
        data: JSON.stringify({content: editedText, record_id: curRecordId}),
        success: function(response) {
            response = JSON.parse(response)
            const logText = response.content
            // 更新原始的日志内容
            log_entry.text(logText);
            log_entry.data('logText', logText);
            processLogEntryText(log_entry)
            // 清空编辑框
            editLog.value = '';
            editLog.curPreObject = null;
            editLog.cur_record_id = null;
            // 关闭模态框
            modal.style.display = "none";
        },
        error: xhr_process_error
    });

}


function editLogEntry(log_entry, record_id) {
    
    // 获取编辑框元素
    var modal = document.getElementById('editLogModal');

    // 获取编辑框中的文本域
    var editLog = document.getElementById('editLog');

    // 如果存在，先删除cur_record_id属性
    if (editLog.hasAttribute('cur_record_id')) {
        editLog.removeAttribute('cur_record_id');
    }

    // 将record_id赋值给editLog的cur_record_id属性
    editLog.setAttribute('cur_record_id', record_id);
    // 将 log_entry 赋值给 editLog 
    editLog.curPreObject = log_entry;

    // 显示模态框
    // modal.style.display = "block";
    modal.style.display = "flex";

    // 将原始日志内容填充到编辑框中
    // var pre_text = getOriginTextFromPre(log_entry);
    // pre_text = restoreLatexFromRendered(log_entry)
    let log_text = log_entry.data('logText')
    editLog.value = removeLogseqMatches(log_text);
    //  
    autoResize('editLog')
}

// 删除日志条目函数
function deleteLogEntry(record_id, logentrycontainer) {
    // 删除日志条目的具体逻辑
    $.ajax({
        url: '/v1/diary-log/deletelog/' + record_id,
        type: 'DELETE',
        // headers: {
        //     'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        // },
        success: function(response) {
            // 请求成功时的处理
            console.log('Logs deleted successfully.');
            logentrycontainer.remove()
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
}


function renderLatexInLog(htmlString) {
    try{
        // 块级公式, 占据一行, 居中显示
        htmlString = htmlString.replace(
            /(?:\s|\r?\n)*?\$\$([\s\S]*?)\$\$(?:\s|\r?\n)*?/g,
            function(match, latexMatch) {
                // 将 HTML 字符串解析为文本, 并去除前后空白字符
                var equation = $("<div>").html(latexMatch).text().trim(); 
                var latexBlock = document.createElement('div');
                latexBlock.classList.add('BlocklatexMath'); // 添加类名
                // 设置为块级公式
                katex.render(equation, latexBlock, { displayMode: true }); 
                return latexBlock.outerHTML; // 返回渲染后的 LaTeX 块
            }
        );   
    } catch(e){
        console.error("Latex Parasing Error");
        console.error(e);
    }

    try{
        htmlString = htmlString.replace(
            /(?:\$|\\\[|\\\()([\s\S]*?)(?:\$|\\\]|\\\))/g,
            function(match, latexMatch) {
                // 将 HTML 字符串解析为文本, 并去除前后空白字符
                var equation = $("<div>").html(latexMatch).text().trim(); 
                var span = document.createElement('span');
                // 不需要为 span 元素添加 data-latex 属性以存储原始的 LaTeX 代码, 
                // 否则 log_entry.html() 再次又包含了 latex 源码, 再次解析会乱码
                // span.setAttribute('data-latex', match); 
                span.classList.add('latexMath'); // 添加类名
                katex.render(equation, span);
                return span.outerHTML;
            }
        );
    } catch(e){
        console.error("Latex Parasing Error");
        console.error(e);
    }

    return htmlString
}


function restoreLatexFromRendered(element) {
    // 使用clone()方法创建元素的副本
    var elementCopy = element.clone();
    // 选择所有超链接元素并替换为其文本内容
    elementCopy.find('.katex').replaceWith(function() {
        // 获取 .katex 元素的 data-latex 属性的值
        var latexCode = $(this).attr('data-latex');
        return ' $$' + latexCode + '$$';
    });
    // 返回修改后的文本内容
    return elementCopy.text();
}


// Function to replace URLs with hyperlinks within a <log_entry> element
function replaceURLsWithLinks(htmlString) {
    // element 是 jQuery 对象
    // Get the text content of the <log_entry> element
    var content = htmlString;
    // Regular expression to find URLs within the text
    var urlRegex = /(?<=^|\s)(https?:\/\/[^\s]+)/g;
    // Replace URLs with hyperlinks
    content = content.replace(urlRegex, function(url) {
      return '<a href="' + url + '">' + url + '</a>';
    });
    // Set the HTML content of the <log_entry> element with the replaced content
    // log_entry.html(content);
    return content
}


// function replaceCodeWithPre(log_entry) {
//     var copyIcon = $(<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy w-4 h-auto"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg>)

//     // 获取<log_entry>元素的文本内容
//     var content = log_entry.html();
    
//     // 定义匹配三个反引号包围的代码段的正则表达式
//     var codeRegex = /```([\s\S]*?)```/g;

//     content = content.replace(codeRegex, function(match, code) {
//         // 移除代码段开头的换行符
//         code = code.replace(/^\n+/, '');
//         code = code.trimEnd();
    
//         if (code.length === 0) {
//             // 空代码段处理方式1：替换为空白
//             return '<pre></pre>';
//         }
    
//         // 使用<pre>标签包裹代码段
//         return '<pre>' + code + '</pre>';
//     });    

//     // 设置<log_entry>元素的HTML内容为替换后的内容
//     log_entry.html(content);
// }

// function copyIconSvgButtonListener(button) {
//     // 为所有的.copyIconSvgButton按钮添加点击事件监听器
//     button.click(function () {

//         // 获取点击按钮所在的code-container元素
//         var codeContainer = $(this).closest('.code-container');

//         // 获取code-container中的pre元素的文本内容
//         var code = codeContainer.find('pre').text();
//         copyToClipboard(removeMinimumIndentation(code))
//         showNotification('Success!', 700);

//         // alert('代码已复制到剪贴板！');
//     });
// }


function copyIconSvgButtonListener(button) {
    let buttonDom = button.get(0)
    let clipboard = new ClipboardJS(buttonDom,{
        text: function(trigger){
            // trigger DOM 元素
            var codeContainer =  trigger.closest('.code-container');
            var code = codeContainer.querySelector('pre').textContent;
            return removeMinimumIndentation(code)
        }
    });
    // 处理复制成功事件（可选）
    clipboard.on('success', function(e) {
        console.log('复制成功');
        showNotification('Copy Success!', 700);
        e.clearSelection();
    });
    
    // 处理复制失败事件（可选）
    clipboard.on('error', function(e) {
        console.error('复制失败：', e.action);
    });
    
}


function replaceCodeWithPre(htmlString) {
    // 定义语言映射表
    const languageMap = {
        'python': 'Python',
        'c': 'C',
        'make': 'Makefile',
        'cmd': 'CMD',
        'sql': 'SQL',
        'db': 'Database',
        'mongodb': 'MongoDB',
        'c#': 'C#',
        'c++': 'C++',
        'objective-c': 'Objective-C',
        'objective-c++': 'Objective-C++',
        'js': 'JavaScript',
        'javascript': 'JavaScript',
        'css': 'CSS',
        'html': 'HTML',
        'php': 'PHP',
        'go': 'Go',
        'ruby': 'Ruby',
        'rust': 'Rust',
        'java': 'Java',
        'shell': 'Shell',
        'sh': 'Shell',
        'code': 'Code',
        'py': 'Python'
    };
    // 复制图标的HTML字符串
    var copyIcon = $(`<div class="copyIcon"> 
    <span class="codeTag">Code</span>
    <button class="copyIconSvgButton">
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy w-4 h-auto"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg>
    </button>
    </div>`);
    
    // 获取<log_entry>元素的文本内容
    var content = htmlString;
    
    // 定义匹配三个反引号包围的代码段的正则表达式
    // var codeRegex = /```([\s\S]*?)```/g;
    // var codeRegex = /```(python|c|c\+\+|js|css|html|go|ruby|java)\s*\n([\s\S]*?)```/g;
    // var codeRegex = /```(python|c|c\+\+|js|css|html|go|ruby|java|(?=))\s*\n([\s\S]*?)```/g
    // var codeRegex = /```((?:python|c|c\+\+|js|css|html|go|ruby|java)?)\s*\n([\s\S]*?)```/g
    // const codeRegex = /```(objective-c\+*|\w*)([^]*)```/gi;
    const codeRegex = /```(objective-c\+*|c#|c\+\+|\w*)([\s\S]*?)```/gi;
    content = content.replace(codeRegex, function(match, language, code) {
        language = language.toLowerCase();
        let languageName = languageMap[language];
      //   let languageName = languageMap[language] || 'None';
        
        // 如果找不到对应的语言名称，将匹配项合并到代码中
        if (!languageName) {
          code = language + code;
        }
        // 移除代码段开头和结尾的换行符
        code = code.replace(/^\n+/, '').trimEnd();
    
        if (code.length === 0) {
            // 空代码段处理方式1：替换为空白
            return '<div class="code-container"><pre></pre></div>';
        }
        if (languageName){
            copyIcon.find('span').text(languageName);
        }

    
        // 使用<div>标签包裹复制图标和<pre>标签
        return `<div class="code-container">${copyIcon.prop('outerHTML')}<pre>${code}</pre></div>`;
    });  

    const singleLineCode = /`([^`]+)`/g;
    content = content.replace(singleLineCode, function(match, code) {
        return `<span class="singleLineCode">${code}</span>`;

    });

    const tagRegex = /(^|\s)#\w+\b/g;
    content = content.replace(tagRegex, function(match) {
        return `<span class="tag">${match}</span>`;

    });

    // 设置<log_entry>元素的HTML内容为替换后的内容
    // log_entry.html(content);
    return content
}

function addCodeBlockCopyListener(log_entry){
    // 获取替换后的代码块元素
    var codeContainers = log_entry.find('.code-container');

    // 为每个代码块元素添加点击事件监听器
    codeContainers.each(function() {
        var button = $(this).find('.copyIconSvgButton');
        if (button.length){ copyIconSvgButtonListener(button); }
    });
}


function replaceTabWithSpace(htmlString) {
    // 获取<log_entry>元素的文本内容
    // var content = log_entry.html();
    var content = htmlString
    
    // 定义匹配\t的正则表达式
    var tabRegex = /\t{1,}/g;

    content = content.replace(tabRegex, function(match) {
        // 使用空格替换
        return '  '.repeat(match.length);
    });    

    // 设置<log_entry>元素的HTML内容为替换后的内容
    // log_entry.html(content);
    return content
}


function removeMinimumIndentation(text) {
    // 将文本分割成行数组
    const lines = text.split('\n');

    // 初始化最小缩进量为一个较大的值
    let minIndentation = Infinity;

    // 遍历每一行，找到最小缩进量，但不处理空行
    for (const line of lines) {
        if (line.trim() === '') {
            continue;
        }

        let indentation = 0;
        while (line[indentation] === ' ') {
            indentation++;
        }

        if (indentation < minIndentation) {
            minIndentation = indentation;
        }
    }

    // 如果所有行都是空行或没有缩进，设置最小缩进为0
    if (minIndentation === Infinity) {
        minIndentation = 0;
    }

    // 去除每行的最小缩进量空格，并忽略完全是空格的行
    const result = lines.map(line => {
        if (line.trim() === '') {
            return line;
        } else {
            return line.slice(minIndentation);
        }
    }).join('\n');

    return result;
}

  
function processLogEntryText(log_entry){
    let htmlString = log_entry.html();
    htmlString = replaceURLsWithLinks(htmlString);
    htmlString = replaceTabWithSpace(htmlString);
    htmlString = replaceCodeWithPre(htmlString);
    htmlString = renderLatexInLog(htmlString)
    log_entry.html(htmlString)
    addCodeBlockCopyListener(log_entry)
}


function getOriginTextFromPre(element) {
    // element 是 jQuery 对象
    // 使用clone()方法创建元素的副本
    var elementCopy = element.clone();
    // 选择所有超链接元素并替换为其文本内容
    elementCopy.find('a').replaceWith(function() {
        // 返回超链接的文本内容
        return this.textContent;
    });
    // 返回修改后的文本内容
    return elementCopy.text();
}


// 使用示例：
// 假设有一个 id 为 logList 的容器，你可以调用 addLogEntry 函数来添加日志条目。
// 例如：
// addLogEntry('这是一条日志信息');
function xhr_process_error(xhr, status, error) {
    // 读取失败时返回的内容
    var statusCode = xhr.status;
    var errorMessage = xhr.responseText;

    if (statusCode === 401) {
        alert("登录已过期，请重新登录");
        console.log("Unauthorized - Redirecting to login page");
        window.location.href = '/v1/diary-log/login';
    } 

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

function addLog() {
    const now = new Date();
    const dateStr = now.toLocaleDateString();
    const timeStr = now.toLocaleTimeString();
    var log = `## ${dateStr} ${timeStr}:\n` + $('#log').val();
    if ($('#log').val() === '') {
        console.log("log is none");
        return; // 退出函数
    }
    
    $.ajax({
        url: '/v1/diary-log/addlog',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({content: log}),
        success: function(response) {
            response = JSON.parse(response)
            addLogEntry(response.content, response.record_id)
            
            // 清空 输入框
            $('#log').val('');
            // console.log(response);
        },
        error: xhr_process_error
    });
}



function getLogs(page_size = null, page_number = null) {
    var get_log_url = '/v1/diary-log/getlogs';
    
    if (page_size !== null && page_number !== null) {
        get_log_url += '?page_size=' + page_size + 
                       '&page_number=' + page_number;
    }
    
    $.ajax({
        url: get_log_url,
        type: 'GET',
        // headers: {
        //     'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        // },
        success: function(response) {
            response = JSON.parse(response);
            page_size = response.page_size;
            page_number = response.page_number;
            localStorage.setItem('page_size', page_size);
            localStorage.setItem('page_number', page_number);

            for (var i = 0; i < response.logs.length; i++) {
                addLogEntry(response.logs[i], response.ids[i], false);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if (jqXHR.status === 401) {
                console.log("Unauthorized - Redirecting to login page");
                window.location.href = '/v1/diary-log/login';
            } else {
                console.log("Other error:", textStatus, errorThrown);
            }
        }
    });
}


function alt_q(event) {
    if (event.altKey && event.key === "q") {
      console.log("alt+q was pressed.");
      var textarea = event.target; // 获取事件的目标元素
      // 在这里编写按下alt+q 后要执行的代码
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        var value = textarea.value;
        var selectedText = value.substring(start, end);
        var indentedText = selectedText.split('\n').map(function(line) {
            const leading_t = '\t'
            return leading_t + line; // 将生成的空格字符串和剩余的字符串拼接返回
        }).join('\n');
        textarea.value = value.substring(0, start) +
                         indentedText + value.substring(end);
        if (selectedText.length){
            textarea.selectionStart = start;
            textarea.selectionEnd = end + 
                (indentedText.length - selectedText.length);
        } else {
            textarea.selectionEnd = end + 
                (indentedText.length - selectedText.length);
            textarea.selectionStart = textarea.selectionEnd;
        }                
    }
};


function tab_to_space(event) {
    if (event.key === "Tab") { // 按下Tab键或Shift+Tab键
        console.log("tab was pressed.");
        var textarea = event.target; // 获取事件的目标元素
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        var value = textarea.value;
        var selectedText = value.substring(start, end);
        var tab_to_space_num = 2

        if (event.shiftKey) { // 按下Shift键 需要反缩进

            // 获取选中文本所在行的起始位置和结束位置
            var lineStart = value.lastIndexOf('\n', start - 1) + 1;
            var lineEnd = value.indexOf('\n', end);
            // 如果选中文本所在行是最后一行，需要特殊处理
            if (lineEnd === -1) {
            lineEnd = value.length;
            }
            // 获取选中文本所在行的所有字符串
            selectedText = value.substring(lineStart, lineEnd);

            var unindentedText = selectedText.split('\n').map(function(line) {
                var leadingTabs = line.match(/^\t+/); // 匹配行首的制表符
                if (leadingTabs) { // 存在制表符
                    // 将制表符替换为四个空格，然后去掉前四个空格或制表符
                    let i = 0;
                    while (line[i] === '\t') {i++;}
                    // const leadingSpaces = '    '.repeat(i); // 生成 i 个空格的字符串
                    const leadingSpaces = ' '.repeat(tab_to_space_num).repeat(i); // 生成 i 个空格的字符串
                    line = leadingSpaces + line.substring(i); // 将生成的空格字符串和剩余的字符串拼接返回
                    return line.substring(4);
                } else if (line.match(/^ {1}/)) { // 前面至少有一个空格时
                    const leadingSpaces = line.match(/^\x20/)[0];
                return line.substring(leadingSpaces.length)
                } else {
                    return line;
                }
            }).join('\n');
            textarea.value = value.substring(0, lineStart) + unindentedText + value.substring(lineEnd);
            var length_d = selectedText.length - unindentedText.length;
            if ((start - length_d) < lineStart){textarea.selectionStart = lineStart}
            else {textarea.selectionStart = start - length_d;}
            textarea.selectionEnd = end - length_d;
        } else { // 没有按下Shift键
            var indentedText = selectedText.split('\n').map(function(line) {
                let i = 0;
                while (line[i] === '\t') {i++;}
                var j = i+1 // 使用4个空格进行正向缩进
                const leadingSpaces = ' '.repeat(tab_to_space_num).repeat(j); // 生成 i 个空格的字符串
                return leadingSpaces + line.substring(i); // 将生成的空格字符串和剩余的字符串拼接返回
            }).join('\n');
            textarea.value = value.substring(0, start) + indentedText + value.substring(end);
            if (selectedText.length){
                textarea.selectionStart = start;
                textarea.selectionEnd = end + (indentedText.length - selectedText.length);
            } else {
                textarea.selectionEnd = end + (indentedText.length - selectedText.length);
                textarea.selectionStart = textarea.selectionEnd;
            }
        }
        event.preventDefault();
    }
};
