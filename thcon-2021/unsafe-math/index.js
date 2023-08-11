// NOTE: I modified this to return JSON instead and added logging for local
// testing. The real server returned form responses, though it didn't matter
const express = require('express');
var engines = require('consolidate');
const bodyParser = require('body-parser');

const app = express();

app.engine('html', engines.mustache);
app.set('view engine', 'html');
app.set('views', __dirname + '/views');
app.use(express.static('static'));
app.use(bodyParser.urlencoded({ extended: true }));

app.get('/', function(req, res){
	return res.render('index', {});
})

app.post('/', function(req, res){
	const regex = /[a-zA-Z]/g;
	var width = req.body.width;
  // console.log(width, typeof width)
	var height = req.body.height;
	if(width === '' || height === ''){
		return res.json({'error':'one of the field is empty...'});
	}
	if(width.length > 10 || height.length > 10){
		return res.json({'error':'width or height are too large !'});
	}
  var evalStr = '(' + width + '**2 + ' + height + '**2) ** (1/2);';
  console.log(evalStr)
	return res.json({'result':'Result: ' + eval(evalStr)});
})

app.listen(3001)
