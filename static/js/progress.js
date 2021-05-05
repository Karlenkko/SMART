//Target and max ==> from DB target<max
var target = window.localStorage.volunteerActual;
var max = 89;

var cnt = document.getElementById("count");
var water = document.getElementById("water");
var value = Number(cnt.innerText);
var interval;
let position = 0;
interval = setInterval(function () {
    value = Number((value + max/100).toFixed(1));
    cnt.innerHTML = value;
    water.style.transform = 'translate(0' + ',' + (100 - position ++) + '%)';
    if (value >= target) {
        cnt.innerHTML = target
        clearInterval(interval);
        //调用展示奖励方法：显示金币等等
    }
}, 60);