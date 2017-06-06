var $ = function (s) {
  return document.querySelector(s);
}
var $$ = function (s) {
  return document.querySelectorAll(s);
}

for (var i = 0; i < $$('.article-date').length; ++i) {
  $$('.article-date')[i].addEventListener('click', function (ev) {
    ev.preventDefault()
    for (var j = 0; j < $$('.article-date').length; ++j) {
      $$('.article-date')[j].className = 'date article-date';
    }
    var idx = ev.target.id.split('-')[2];
    $('#article-date-' + idx).className += ' select';
    $('#list-date-' + idx).className += ' select';
  });
}

for (var i = 0; i < $$('#chosen-date li a').length; ++i) {
  $$('#chosen-date li a')[i].addEventListener('click', function (ev) {
    ev.preventDefault();
    ev.target.parentNode.parentNode.parentNode.removeChild(ev.target.parentNode.parentNode)
  });
}

$('#add').addEventListener('click', function (ev) {
  ev.preventDefault();

  var li = document.createElement('li');
  li.id = '#chosen-date-' + $$('#chosen-date li').length + '-li';
  var a = document.createElement('a');
  a.id = '#chosen-date-' + $$('#chosen-date li').length;
  a.setAttribute('href', '#');
  a.className = 'date';
  var span = document.createElement('span');
  var text = document.createTextNode($('#typein').value);
  span.appendChild(text);
  var input = document.createElement('input');
  input.setAttribute('type', 'hidden');
  input.value = $('#typein').value;
  input.setAttribute('name', 'chosen-date')

  a.appendChild(span);
  a.appendChild(input);
  li.appendChild(a);

  a.addEventListener('click', function (ev) {
    ev.preventDefault();
    li.parentNode.removeChild(li);
  });

  $('#chosen-date').appendChild(li);
  $('#typein').value = '';
})
