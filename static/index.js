var $ = function (s) {
  return document.querySelector(s);
}
var $$ = function (s) {
  return document.querySelectorAll(s);
}

$('#search-time-box').addEventListener('submit', function(ev) {
  ev.preventDefault();

  var has_blank = false;
  var not_number = false;

  for (var i = 0; i < $$('#search-time-box input').length; ++i) {
    var str = String($$('#search-time-box input')[i].value);

    // Check if any input is blank
    if (str.length == 0) {
      has_blank = true;
      break;
    }

    // Check if any input contains non-number
    var check = /\d*/.test(str);
    if (!check) {
      not_number = true;
      break;
    }
  }

  if (has_blank) {
    alert('未完整填寫搜尋欄位！');
  } else if (not_number) {
    alert('搜尋欄位包含非阿拉伯數字！');
  } else {
    ev.target.submit();
  }
})

$('#search-time-box #cancel').addEventListener('click', function(ev) {
  ev.preventDefault();
  for (var i = 0; i < $$('#search-time-box input').length; ++i) {
    $$('#search-time-box input')[i].value = '';
  }
  $('#search-time-box').submit();
})
