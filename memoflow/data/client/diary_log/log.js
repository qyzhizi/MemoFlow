function addLogEntry(logText, record_id) {
    var pre = $('<pre class="log-entry"></pre>'); // 添加一个类以便样式控制
    // 将 pre 元素的内容添加到 pre 中
    pre.text(logText);
    replaceURLsWithLinks(pre);
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
    var latexView = $('<div class="dropdown-option delete-option">latexView</div>');

    // 将下拉菜单图标添加到 dropdownContainer 中
    dropdownContainer.append(dropdownIcon);
    // 将下拉菜单添加到 dropdownContainer 中
    dropdownContainer.append(dropdownMenu);
    // 将 dropdownContainer 添加到 logEntryContainer 中
    logEntryContainer.append(dropdownContainer);
    // 将 pre 添加到 logEntryContainer 中
    logEntryContainer.append(pre);
    // 将 logEntryContainer 添加到 logList 中
    var logList= $('#logList');
    logList.prepend(logEntryContainer);

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
    copyOption.click(function() {
        // 复制日志文本到剪贴板
        copyToClipboard(removeLogseqMatches(pre.text()));
        // 隐藏下拉菜单
        dropdownMenu.hide()
    });

    // 添加编辑选项点击事件处理程序
    editOption.click(function() {
        record_id = dropdownMenu.data('record_id')
        console.log("record_id : ", record_id)
        // 编辑日志条目
        editLogEntry(pre, record_id);
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
            deleteLogEntry(record_id);
            // 删除日志条目
            logEntryContainer.remove();
            // 隐藏下拉菜单
            dropdownMenu.hide();
        }
    });

    // latexView 选项点击事件处理程序
    latexView.click(function() {
        // 渲染当前笔记中出现的公式
        renderLatexInLog(pre);
        // 隐藏下拉菜单
        dropdownMenu.hide();
    });


    // 将复制、编辑和删除选项添加到下拉菜单中
    dropdownMenu.append(copyOption);
    dropdownMenu.append(editOption);
    dropdownMenu.append(deleteOption);
    dropdownMenu.append(latexView);
}


/**
 * 将字符串根据给定的模式分割，并返回匹配项和分隔符的列表
 * @param {string} inputString - 要分割的字符串
 * @param {RegExp} pattern_t - 用于分割字符串的正则表达式模式
 * @returns {string[]} - 包含匹配项和分隔符的列表
 */
function splitStringWithPattern(inputString, pattern_t) {
    let match;
    let match_list = [];
    let old_index = 0;

    while ((match = pattern_t.exec(inputString)) !== null) {
        match_list.push(inputString.substring(old_index, match.index));
        match_list.push(match[0]);
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
        index = i
        strings_index = i +1
        pattern_logseq = process_input[i]
        child_string = process_input[strings_index]
        // 将pattern_logseq 按 “-” 分割
        pattern_logseq = pattern_logseq.split("-")
        num_t_logseq = pattern_logseq[0].length

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


// 取消 Logseq 格式
function removeLogseqMatches(inputString) {
    pattern_logseq_mian = /^[\x20]{0,}\t{0,}-[\x20]/gm
    pattern_logseq_child = /^[\x20]{0,}\t{0,}[\x20]{2}/gm;
    var result1 = splitStringWithPattern(inputString, pattern_logseq_mian);
    inputString = processInputAndReturnString(result1, pattern_logseq_child)

    // 匹配行首的 "  " "\t  " "\t\t  " "\t\t\t  " 等等, 替换为空串
    const pattern = /^[\x20]{0,}\t{0,}[\x20]{2}/gm;
    String1 = inputString.replace(pattern, '')

    // 使用正则表达式进行划分
    var regex = /^\t-[\x20]#ans/gm;
    const pattern_t = /^\t- #/gm;
    var splittedParts = String1.split(regex);
    // 判断splittedParts 的长度是否大于 2
    if (splittedParts.length > 2) {
        console.log("输入字符串中包含多个 #ans");
        // 使用alert()函数进行错误提示
        alert("字符串中包含多个 #ans, 编辑失败");
        // 报错，解析错误
        // throw new Error("字符串中包含多个 #ans");
    }
    // 如果长度为 1，说明字符串中没有包含 #ans
    if (splittedParts.length === 1) {
        result = splittedParts[0].replace(pattern_t, '#');
        console.log("输入字符串中没有包含 #ans");
        return result.substring(2);
    }
    // 如果长度为 2，说明字符串中包含了 #ans
    if (splittedParts.length === 2) {
        console.log("输入字符串中包含了 #ans");
        splittedParts[0] = splittedParts[0].replace(pattern_t, '#');

        part1 = splittedParts[0];
        part2 = splittedParts[1];
        const pattern2_0 = /^[\x20]{0,}\t-[\x20]/gm;
        const pattern2_1 = /^[\x20]{0,}\t\t-[\x20]/gm;
        const pattern2_2 = /^[\x20]{0,}\t\t\t-[\x20]/gm;
        part2 = part2.replace(pattern2_0, '@blk ');
        part2 = part2.replace(pattern2_1, '- ');
        part2 = part2.replace(pattern2_2, '@blk- ');
        result = part1 +"#ans"+ part2;
        return result.substring(2);
    }
}

// 复制到剪贴板函数
function copyToClipboard(text) {
    // 创建一个新的 ClipboardItem 对象
    const clipboardItem = new ClipboardItem({ "text/plain": new Blob([text], { type: "text/plain" }) });
  
    // 将文本添加到剪贴板
    navigator.clipboard.write([clipboardItem]).then(function() {
      console.log('文本已成功复制到剪贴板');
    }).catch(function(err) {
      console.error('复制失败:', err);
    });
  }

function editLogEntry(pre, record_id) {
    // 获取编辑框元素
    var modal = document.getElementById('editLogModal');

    // 获取编辑框中的文本域
    var editLog = document.getElementById('editLog');

    // 显示模态框
    modal.style.display = "block";

    // 获取保存按钮
    var saveChangesBtn = document.getElementById('saveChangesBtn');

    // 获取关闭按钮，并为其添加点击事件处理程序
    var closeBtn = document.getElementsByClassName("close")[0];
    closeBtn.onclick = function() {
        // 弹出窗口提示是否提交
        var confirmation = confirm("是否关闭编辑页面？");

        // 如果用户点击确定按钮
        if (confirmation) {
            // 清空编辑框
            editLog.value = '';
            // 关闭模态框
            modal.style.display = "none";
        } 

    }

    // 当用户点击模态框外部区域时，关闭模态框
    window.onclick = function(event) {
        if (event.target == modal) {
            // 弹出窗口提示是否提交
            var confirmation = confirm("是否关闭编辑页面？");

            // 如果用户点击确定按钮
            if (confirmation) {
                // 清空编辑框
                editLog.value = '';
                // 关闭模态框
                modal.style.display = "none";
            } else {
                // 如果用户点击取消按钮，则什么也不做
                // 用户选择不保存，取消关闭操作
            }
        }
    }
    // 当用户点击保存按钮时
    saveChangesBtn.onclick = function() {
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
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
            },
            contentType: 'application/json',
            data: JSON.stringify({content: editedText, record_id: record_id}),
            success: function(response) {
                response = JSON.parse(response)
                reponseText = response.content
                // 更新原始的日志内容
                pre.text(reponseText);
                replaceURLsWithLinks(pre)
                // 清空编辑框
                editLog.value = '';
                // 关闭模态框
                modal.style.display = "none";
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR);

                if (jqXHR.status === 401) {
                    // 提示登录已过期
                    alert("登录已过期，请重新登录");
                    // HTTPUnauthorized error
                    console.log("Unauthorized - Redirecting to login page");
                    window.location.href = '/v1/diary-log/login.html';
                } else {
                    // Handle other error types as needed
                    console.log("Other error:", textStatus, errorThrown);
                }
            }
        });

    }

    // 将原始日志内容填充到编辑框中
    pre_text = getOriginTextFromPre(pre);
    pre_text = restoreLatexFromRendered(pre)
    editLog.value = removeLogseqMatches(pre_text);
}

// 删除日志条目函数
function deleteLogEntry(record_id) {
    // 删除日志条目的具体逻辑
    $.ajax({
        url: '/v1/diary-log/deletelog/' + record_id,
        type: 'DELETE',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        },
        success: function(response) {
            // 请求成功时的处理
            console.log('Logs deleted successfully.');
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
    
            if (jqXHR.status === 401) {
                // 提示登录已过期
                alert("登录已过期，请重新登录");
                // HTTPUnauthorized error
                console.log("Unauthorized - Redirecting to login page");
                window.location.href = '/v1/diary-log/login.html';
            } else {
                // Handle other error types as needed
                console.log("Other error:", textStatus, errorThrown);
            }
        }
    });
}


// 渲染 Latex 公式
function renderLatexInLog(pre){
    // 获取原始的 LaTeX 公式内容
    var latexContent = pre.html();
    // 提取 LaTeX 公式
    var latexEquations = latexContent.match(
        /(\s\$\$[\s\S]*?\$\$|\s\$[\s\S]*?\$)/g);
    // 判断 latexEquations 是否为 null
    if (latexEquations === null) {
        return;
    }
    // 渲染 LaTeX 公式
    latexEquations.forEach(function(eq) {
        var equation = eq.substring(1, eq.length); // 去除开头的空白符号
        equation = equation.replace(/^(\$+)|(\$+)$/g, '');// 去除 "$$" 符号
        equation = equation.trim(); // 去除前后空白字符
        var span = document.createElement('span');
        katex.render(equation, span);
        span.className = 'katex';
        // 为 span 元素添加 data-latex 属性以存储原始的 LaTeX 代码
        span.setAttribute('data-latex', equation);
        latexContent = latexContent.replace(eq, span.outerHTML);
    });
    // 将替换后的内容放回原始元素中
    pre.html(latexContent);
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


// Function to replace URLs with hyperlinks within a <pre> element
function replaceURLsWithLinks(pre_element) {
    // element 是 jQuery 对象
    // Get the text content of the <pre> element
    var content = pre_element.html();
    // Regular expression to find URLs within the text
    var urlRegex = /(?<=^|\s)(https?:\/\/[^\s]+)/g;
    // Replace URLs with hyperlinks
    content = content.replace(urlRegex, function(url) {
      return '<a href="' + url + '">' + url + '</a>';
    });
    // Set the HTML content of the <pre> element with the replaced content
    pre_element.html(content);
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


$(function() {
    $('#submit').on('click', function(event) {
        event.preventDefault();
        const now = new Date();
        const dateStr = now.toLocaleDateString();
        const timeStr = now.toLocaleTimeString();
        var log = `## ${dateStr} ${timeStr}:\n`+ $('#log').val();
        if ($('#log').val() === '') {
            console.log("log is none")
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
            error: function(error) {
                console.log(error);
            }
        });
    });
    $('#pull').on('click', function(event) {
        event.preventDefault();
        // ask for confirmation
        if (!confirm("Are you sure to pull files from github?")) {
            return;
        }
        $.ajax({
            url: '/v1/diary-log/sync-contents-from-repo-to-db',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
            },
            success: function(response) {
                console.log(response);
                // pop up a dialog
                alert(response);
                // reload the page
                window.location.reload();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR);
        
                if (jqXHR.status === 401) {
                    // 提示登录已过期
                    alert("登录已过期，请重新登录");
                    // HTTPUnauthorized error
                    console.log("Unauthorized - Redirecting to login page");
                    window.location.href = '/v1/diary-log/login.html';
                } else {
                    // Handle other error types as needed
                    console.log("Other error:", textStatus, errorThrown);
                }
            }
        });
    });
    $.ajax({
        url: '/v1/diary-log/getlogs',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        },
        success: function(response) {
            // console.log(response);
            response = JSON.parse(response)
            for (var i = 0; i < response.logs.length; i++) {
                addLogEntry(response.logs[i], response.ids[i]);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
    
            if (jqXHR.status === 401) {
                // 不该提示，不然每开一个页面浏览器插件会不停弹窗提示
                // alert("登录已过期，请重新登录");
                // HTTPUnauthorized error
                console.log("Unauthorized - Redirecting to login page");
                window.location.href = '/v1/diary-log/login.html';
            } else {
                // Handle other error types as needed
                console.log("Other error:", textStatus, errorThrown);
            }
        }
    });

    $('#delete_all').on('click', function(event) {
        event.preventDefault();
        // var log = $('#log').val();
        $.ajax({
            url: '/v1/diary-log/delete_all_log',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
            },
            success: function(response) {
                var logList= $('#logList');
                logList.html("");
                // console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
    
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
            textarea.value = value.substring(0, start) + indentedText + value.substring(end);
            if (selectedText.length){
                textarea.selectionStart = start;
                textarea.selectionEnd = end + (indentedText.length - selectedText.length);
            } else {
                textarea.selectionEnd = end + (indentedText.length - selectedText.length);
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
                        j = i+1 // 使用4个空格进行正向缩进
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
        if (modal.style.display === "block") {
            // 显示提示框
            event.preventDefault();
            // beforeunload 事件的返回值
            event.returnValue = " ";
        }
    });

});
