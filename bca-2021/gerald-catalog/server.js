#!/usr/bin/env node
const express = require('express');
const morgan = require('morgan');

const app = express();
app.use(morgan('dev'));

app.post('/', function(req, res){
  res.set('Location', 'http://localhost:1337/gerald/153d4759-fe68-48bc-a83b-283d03497b25';);
  res.status(301);
  return res.send();
});

app.listen(8000);
