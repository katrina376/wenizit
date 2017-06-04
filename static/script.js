var $ = function (s) {
  return document.querySelector(s);
}
var $$ = function (s) {
  return document.querySelectorAll(s);
}

var dates = $$('.date');

for (var i = 0; i < dates.length; ++i) {
  dates[i].addEventListener('click', function (ev) {
    ev.preventDefault()
    $('#chosen').value = ev.target.innerHTML;
    for (var j = 0; j < dates.length; ++j) {
      dates[j].className = 'date';
    }
    var idx = ev.target.id.split('-')[2];
    $('#article-date-' + idx).className += ' chosen';
    $('#list-date-' + idx).className += ' chosen';
  });
}

$('#chosen').addEventListener('input', function (ev) {
  for (var i = 0; i < dates.length; ++i) {
    dates[i].className = 'date';
  }
})
