var CryptoJS = require('crypto-js');

function encryptByDES(message, key){
    var keyHex = CryptoJS.enc.Utf8.parse(key);
    var encrypted = CryptoJS.DES.encrypt(message, keyHex, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    });
    return encrypted.ciphertext.toString();
}


function base64Handle(opts) {
    const { data, type, unicode } = opts;
    let str = data;

    // unicode:true 先转utf-8，解决中文乱码
    if (unicode) {
        if (type === 0) {
            // 编码：字符串 → utf8 → base64
            str = encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, (_, p1) => String.fromCharCode('0x' + p1));
            return btoa(str);
        } else {
            // 解码：base64 → utf8 → 原字符串
            str = atob(str);
            return decodeURIComponent(str.split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
        }
    } else {
        // 不开启unicode兼容
        return type === 0 ? btoa(str) : atob(str);
    }
}

// 等价你原来的代码 var cookieU=$.base64({data: userID,type:0,unicode:true})

function get_Username(id) {
        return base64Handle({
        data: id,
        type: 0,
        unicode: true
    });
}
userID = '2050061020000219'
console.log('cookieU:', get_Username(userID));