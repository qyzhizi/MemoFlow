async function set_user_name_and_avatar(containerId) {
    var url = '/v1/diary-log/get-user-avatar-image';
    try {
        // 使用 await 等待异步操作完成
        let response = await $.ajax({
            url: url,
            type: 'GET'
        });

        // 处理响应
        if (typeof response === 'string') {
            // 如果response是字符串，尝试解析它
            try {
                response = JSON.parse(response);
            } catch (e) {
                console.error("解析错误", e);
                throw e; // 抛出异常，以便调用者可以捕获
            }
        }
        
        var username = response.username;
        var base64Data = response.avatar_image;
        // 使用jQuery选择器获取div元素
        let $div = $("#" + containerId).find('.user-info').first();;

        let $newSpan, $newImg;

        // 检查 response 对象中是否存在 username 和 avatar_image 属性
        if (response.username) {
            // 创建新的span元素并设置其文本内容
            $newSpan = $('<span>').text(username);
        } else {
            $newSpan = $('<span>').text("");
        }
        
        if (response.avatar_image) {
            // 创建新的img元素并设置其属性
            $newImg = $('<img>').attr({
                // src: 'data:image/png;base64,' + base64Data,
                src: base64Data,
                alt: 'Avatar'
            });
        } else {
            $newImg = $('<img>').attr({
                src: "https://via.placeholder.com/150",
                alt: "Avatar"
            });
        }
        
        // 清空div的当前内容并添加新的img和span元素
        $div.empty().append($newImg, $newSpan);

    } catch (error) {
        console.error("请求失败", error);
        throw error; // 抛出异常，以便调用者可以捕获
    }
};


async function getUserNameAndAvatar(url) {
    // var url = '/v1/diary-log/get-user-avatar-image';
    try {
        // 使用 await 等待异步操作完成
        let response = await $.ajax({
            url: url,
            type: 'GET'
        });

        // 处理响应
        if (typeof response === 'string') {
            // 如果response是字符串，尝试解析它
            try {
                response = JSON.parse(response);
            } catch (e) {
                console.error("解析错误", e);
                throw e; // 抛出异常，以便调用者可以捕获
            }
        }
        
        var username = response.username;
        var base64Data = response.avatar_image;

        // 创建一个虚拟的 div 元素
        // var avatarUsernameDiv = document.createElement('div');
        var avatarUsernameDiv = $('<div></div>');

        let $newSpan, $newImg;

        // 检查 response 对象中是否存在 username 和 avatar_image 属性
        if (response.username) {
            // 创建新的span元素并设置其文本内容
            $newSpan = $('<span>').text(username);
        } else {
            $newSpan = $('<span>').text("");
        }
        
        if (response.avatar_image) {
            // 创建新的img元素并设置其属性
            $newImg = $('<img>').attr({
                // src: 'data:image/png;base64,' + base64Data,
                src: base64Data,
                alt: 'Avatar'
            });
        } else {
            $newImg = $('<img>').attr({
                src: "https://via.placeholder.com/50",
                alt: "Avatar"
            });
        }
        
        // 清空div的当前内容并添加新的img和span元素
        avatarUsernameDiv.append($newImg, $newSpan);
        return avatarUsernameDiv;

    } catch (error) {
        console.error("请求失败", error);
        throw error; // 抛出异常，以便调用者可以捕获
    }
};

// input upload file, then evt 
function cropImage(evt) {
    return new Promise((resolve, reject) => {
        var files = evt.target.files;
        // FileReader support
        if (FileReader && files && files.length) {
            Image2base64(files[0]).then((base64) => {
                // 创建一个新的 Image 对象，并将其大小设置为 100x100
                var newImg = new Image();
                newImg.onload = function() {
                    newImg.width = 100;
                    newImg.height = 100;
                    // 返回处理后的图片
                    resolve(newImg);
                };
                newImg.src = base64;
            }).catch((error) => {
                reject(error);
            });
        }
    });
};


function Image2base64(file){
    return new Promise((resolve, reject) => {
         // 如果 file 为空，则直接返回空字符串
         if (!file) {
            resolve('');
            return;
        }
        if (FileReader && file) {
            var fr = new FileReader();
            fr.onload = function () {
                var img = new Image();
                img.onload = function() {
                    var canvas = document.createElement('canvas');
                    var ctx = canvas.getContext('2d');

                    // 计算裁剪后的正方形区域
                    var size = Math.min(img.width, img.height); 
                    var x = (img.width - size) / 2;
                    var y = (img.height - size) / 2;

                    // 在 canvas 上绘制裁剪后的图片
                    canvas.width = size;
                    canvas.height = size;
                    ctx.drawImage(img, x, y, size, size, 0, 0, size, size);

                    // 计算缩放后的尺寸
                    var scaleFactor = 100 / size;
                    var width = size * scaleFactor;
                    var height = size * scaleFactor;

                    // 创建新的 canvas 用于缩放
                    var scaledCanvas = document.createElement('canvas');
                    var scaledCtx = scaledCanvas.getContext('2d');
                    scaledCanvas.width = width;
                    scaledCanvas.height = height;
                    scaledCtx.drawImage(canvas, 0, 0, size, size, 0, 0, width, height);

                    // 将 canvas 中的图像转换为 base64 字符串
                    // 可以修改图片格式为其他格式，比如image/png
                    var base64 = scaledCanvas.toDataURL('image/jpeg'); 
                    resolve(base64);
                };
                img.src = fr.result;
            };
            fr.readAsDataURL(file);
        };
    });
};

function showup_class(class_name){
    class_name = '.' + class_name.split(' ').join('.');
    $(class_name).removeClass('showoff').addClass('showup');
};

function showoff_class(class_name){
    class_name = '.' + class_name.split(' ').join('.');
    $(class_name).removeClass('showup').addClass('showoff');
};

// function showNotification(message) {
//     const notification = document.createElement("div");
//     notification.innerText = message;
//     notification.style.position = "fixed";
//     notification.style.bottom = "20px";
//     notification.style.right = "20px";
//     notification.style.backgroundColor = "green";
//     notification.style.color = "white";
//     notification.style.padding = "10px";
//     notification.style.borderRadius = "5px";
//     notification.style.zIndex = "1000";
  
//     document.body.appendChild(notification);
  
//     setTimeout(() => {
//       document.body.removeChild(notification);
//     }, 3000); // 3秒后自动消失
//   }
function showNotification(message, time) {
    const notification = document.createElement("div");
    notification.style.position = "fixed";
    notification.style.top = "20px";
    notification.style.right = "20px";
    notification.style.backgroundColor = "white"; // 背景色改为白色
    notification.style.color = "black";
    notification.style.padding = "10px";
    notification.style.borderRadius = "5px";
    notification.style.zIndex = "1000";
    notification.style.boxShadow = "0 4px 8px rgba(0,0,0,0.1)"; // 可选：添加一些阴影以增加立体感
    notification.style.display = "flex";
    notification.style.alignItems = "center";
  
    // 创建对勾元素
    const checkMark = document.createElement("span");
    checkMark.innerHTML = "&#10004;"; // 对勾符号
    checkMark.style.color = "green"; // 对勾颜色为绿色
    checkMark.style.marginRight = "10px"; // 与文本保持一定距离
  
    // 创建文本元素
    const text = document.createElement("span");
    text.innerText = message;
  
    // 将对勾和文本加入到通知中
    notification.appendChild(checkMark);
    notification.appendChild(text);
  
    document.body.appendChild(notification);
  
    setTimeout(() => {
      document.body.removeChild(notification);
    }, time); // 3秒后自动消失
}


async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.text(); // 或者使用 response.json() 如果返回的是 JSON 数据
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}




// // 调用函数开始获取并处理数据
// processData();

// param: sourceDivData classInSourceDiv targetDivData TargetDivClass
// process: sourceDivData.classInSourceDiv -> targetDivData.TargetDivClass
// return targetDivData innerHTML
function addSourceDataToTargetDiv(options) {
    // 获取参数
    var sourceDivData = options.sourceDivData;
    var idInSourceDiv = options.idInSourceDiv;
    var classInSourceDiv = options.classInSourceDiv;
    var targetDivData = options.targetDivData;
    var idInTargetDiv = options.idInTargetDiv;
    var TargetDivClass = options.TargetDivClass;
    var placeFirst = options.placeFirst;
    var placeLast = options.placeLast;

    // 创建一个临时 div 元素来处理 sourceDivData
    var sourceDiv = document.createElement('div');
    sourceDiv.innerHTML = sourceDivData;

    // 获取 sourceDiv 中的指定容器
    var container;
    if (idInSourceDiv){
        container = sourceDiv.querySelector('#' + idInSourceDiv);}
    else if (classInSourceDiv) {
        container = sourceDiv.querySelector('.' + classInSourceDiv);}   

    // 如果 idInSourceDiv or classInSourceDiv 所属容器不存在，那么设置为 sourceDiv
    if (!container) {
         container = sourceDiv.querySelector('div');

    }

    // 创建一个临时 div 元素来处理 targetDivData
    var targetDiv = document.createElement('div');
    targetDiv.innerHTML = targetDivData;

    // 获取 targetDiv 中的指定容器
    if (idInTargetDiv){
        var targetContainer = targetDiv.querySelector('#' + idInTargetDiv);}
    else if (TargetDivClass) {
        var targetContainer = targetDiv.querySelector('.' + TargetDivClass);}

    // 将 sourceDiv 中指定容器的内容添加到另一个 div 的指定容器中
    if (!targetContainer) {
        targetContainer = document.createElement('div');
        if (TargetDivClass) {
            targetContainer.className = TargetDivClass;
        }
        // if (placeLast) {targetDiv.appendChild(targetContainer)}
        // if (placeFirst) {targetDiv.insertBefore(targetContainer, targetDiv.firstChild)}
    }
    // 注意 outerHTML 与 innerHTML 区别
    // targetContainer.innerHTML = container.outerHTML;
    if (placeLast) {targetContainer.appendChild(container)}
    // if (placeFirst) {targetContainer.insertBefore(container, targetDiv.firstChild)}
    if (placeFirst) {targetContainer.prepend(container);}

    // 返回另一个 div 的 innerHTML 数据
    return targetDiv.innerHTML;
}


function addDivInnerHTMLToBodyContainer(options) {
    // 提取参数对象中的属性
    var doc_data = options.doc_data;
    var container_id = options.container_id;
    // 检查指定的容器是否存在
    var container = document.getElementById(container_id);
    if (!container) {
        // 如果容器不存在，则创建一个新的 div 容器，并将其添加到 body 中
        container = document.createElement('div');
        container.id = container_id;
        document.body.appendChild(container);
    }

    // 创建一个临时div来存放加载的HTML，以便查询特定元素
    var tempDiv = document.createElement('div');
    tempDiv.innerHTML = doc_data;

    // 提取并移除 <style> 元素
    var styles = tempDiv.querySelectorAll('style');
    Array.from(styles).forEach(style => {
        document.head.insertAdjacentHTML('beforeend', `<style>${style.textContent}</style>`);
        style.remove();
    });

    // 从加载的HTML中提取特定元素
    var specificElement = tempDiv.querySelector('div');

    // 创建一个新的 div 容器
    var containerDiv = document.createElement('div');
    // 将 specificElement 添加到新创建的 containerDiv 中
    containerDiv.appendChild(specificElement);
    // 将这个包含 specificElement 的 containerDiv 添加到指定的容器中
    container.appendChild(containerDiv);
};


function checkElementExistence(element_id) {
    // 获取 id 的容器
    var container = document.getElementById(element_id);
    let container_exist = null;
    // 检查是否找到容器
    if (container !== null) {
        console.log('找到 id 为 "' + element_id + '" 的容器。');
        container_exist = true;
    } else {
        container_exist = false;
        console.log('未找到 id 为 "' + element_id + '" 的容器。');
    };
    return container_exist;
};


// Pattern 必须保证有一个分组
function textMatchPattern(input, Pattern, PatternType) {
    let match;
    let Matches = [];
    let lastIndex = 0; // 用于跟踪上一个匹配项的结束位置

    // 搜集所有行间代码块及其位置
    while ((match = Pattern.exec(input)) !== null) {
        // 检查并添加前一个代码块后和当前代码块前的非代码块文本
        let fullMatchIndex = match.index; // 总匹配的起始位置
        let firstGroupIndex = fullMatchIndex + match[0].indexOf(match[1]); // 第一个分组的起始位置
        if (firstGroupIndex > lastIndex) {
            Matches.push({
                type: 'text',
                content: input.substring(lastIndex, firstGroupIndex),
            });
        }

        Matches.push({
            type: PatternType,
            content: match[1],
        });

        // 更新lastIndex为当前代码块的结束位置
        lastIndex = firstGroupIndex + match[1].length;
    }

    // 检查最后一个代码块后是否还有文本
    if (lastIndex < input.length) {
        Matches.push({
            type: 'text',
            content: input.substring(lastIndex),
        });
    }
    return Matches;
}


function subTextMatchPattern(Matches, Pattern, PatternType){
    let tempMatches = [...Matches];
    for(let i = 0, addItems = 0; i < tempMatches.length; i++){
        let item  = tempMatches[i];
        if (item.type == 'text'){
            let PatternMatches = textMatchPattern(item.content, Pattern, PatternType);
            Matches.splice(i + addItems, 1, ...PatternMatches)
            addItems = addItems + PatternMatches.length - 1
        }
    }
}


function mulTextMatchPattern(input, codeBlockLinesPattern, inlinePattern, otherPatterns){
    let Matches = textMatchPattern(input, codeBlockLinesPattern.regex, codeBlockLinesPattern.type);
    subTextMatchPattern(Matches, inlinePattern.regex, inlinePattern.type)
    otherPatterns.forEach(element => {
        subTextMatchPattern(Matches, element.regex, element.type)
    }); 
    return Matches
}


export {
    set_user_name_and_avatar,
    cropImage, Image2base64, showup_class, showoff_class,
    showNotification,
    addDivInnerHTMLToBodyContainer,
    checkElementExistence,
    addSourceDataToTargetDiv,
    fetchData,
    getUserNameAndAvatar,
    mulTextMatchPattern,
};