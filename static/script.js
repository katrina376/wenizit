var $ = function (s) {
  return document.querySelector(s);
}
var $$ = function (s) {
  return document.querySelectorAll(s);
}

var add_date = function (value) {
  var li = document.createElement('li');
  li.id = '#chosen-date-' + $$('#chosen-date li').length + '-li';
  var a = document.createElement('a');
  a.id = '#chosen-date-' + $$('#chosen-date li').length;
  a.setAttribute('href', '#');
  a.className = 'date';
  var span = document.createElement('span');
  var text = document.createTextNode(value);
  span.appendChild(text);
  var input = document.createElement('input');
  input.setAttribute('type', 'hidden');
  input.value = value;
  input.setAttribute('name', 'chosen-date')

  a.appendChild(span);
  a.appendChild(input);
  li.appendChild(a);

  a.addEventListener('click', function (ev) {
    ev.preventDefault();
    li.parentNode.removeChild(li);
  });

  $('#chosen-date').appendChild(li);
}

for (var i = 0; i < $$('.article-date').length; ++i) {
  $$('.article-date')[i].addEventListener('click', function (ev) {
    ev.preventDefault()
    for (var j = 0; j < $$('.article-date').length; ++j) {
      $$('.article-date')[j].className = 'date article-date';
    }
    var idx = ev.target.id.split('-')[2];
    $('#article-date-' + idx).className += ' select';
    add_date($('#article-date-' + idx).textContent)
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
  add_date($('#typein').value);
  $('#typein').value = '';
})

$('#save').addEventListener('click', function (ev) {
  ev.preventDefault();
  if ($$('#chosen-date li').length < 1) {
    alert('未選擇日期！');
  } else {
    $('#form-date').submit();
  }
})
