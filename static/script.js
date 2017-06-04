var $ = function (s) {
  return document.querySelector(s);
}
var $$ = function (s) {
  return document.querySelectorAll(s);
}

$$('.date').forEach(function (it) {
  it.addEventListener('click', function (ev) {
    ev.preventDefault()
    $('#chosen').value = ev.target.innerHTML;
    $$('.date').forEach(function (itt) {itt.className = 'date'; });
    var idx = ev.target.id.split('-')[2]
    $('#article-date-' + idx).className += ' chosen'
    $('#list-date-' + idx).className += ' chosen'
  })
})
