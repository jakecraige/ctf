const bodyParser = require('body-parser');
const cors = require('cors');
const express = require('express');
const fetch = require('node-fetch');
const mysql = require('mysql');
const puppeteer = require('puppeteer');
const queue = require('queue');

const connection = mysql.createConnection({
    host: process.env.MYSQL_HOST || '127.0.0.1',
    user: "securecash",
    database: "securecash"
});

var q = queue();
q.timeout = 1000;
q.concurrency = 1;
q.autostart = true;
q.on("timeout", function (next, job) {
    console.log('Job timed out:', job.toString().replace(/\n/g, ''));
    next();
});
q.on("success", function (result, job) {
    console.log('Job finished processing:', job.toString().replace(/\n/g, ''))
});

const BIND_ADDR = process.env.BIND_ADDR || '0.0.0.0';
const PORT = process.env.PORT || '1337';
var ADMIN_PAGE;

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cors());

function sendError(response, responseCode, errorMessage, errorDetails) {
    errorMessage = errorMessage || "Internal server error";
    responseCode = responseCode || 500;
    errorDetails = errorDetails || {};

    let message = {
        code: responseCode,
        status: "error",
        details: errorDetails,
        errorMessage: errorMessage
    }

    response.status(responseCode);
    response.json(message);
    response.end();
}

function sendSuccess(response, responseData, responseCode) {
    responseCode = responseCode || 200;
    responseData = responseData || {};

    let message = {
        code: responseCode,
        data: responseData,
        status: "success"
    }

    response.status(responseCode);
    response.json(message);
    response.end();
}

function getAdminToken() {
    return new Promise((resolve, reject) => {
        connection.query('SELECT api_key FROM general WHERE admin=true;', (err, data) => {
            if (err) {
                reject(err);
            }
            if (data) {
                resolve(data[0].api_key);
            }
        });
    });
}

async function adminLookup(cb, url) {
    if (!ADMIN_PAGE) {
        token = await getAdminToken();
        ADMIN_PAGE = `http://app:1337/?api_key=${token}`;
        console.log("Caching admin token:", token);
    }

    const browser = await puppeteer.launch({
        executablePath: process.env.CHROMIUM_PATH,
        args: ['--no-sandbox']
      });
    const page = await browser.newPage();
    page
      .on('console', message =>
        console.log(`${message.type().substr(0, 3).toUpperCase()} ${message.text()}`))
      .on('pageerror', ({ message }) => console.log('PAGERROR', message))
    .on('response', response => {
      if (response.url().endsWith("png") || response.url().endsWith("js") || response.url().endsWith("css") || response.url().endsWith("jpg") || response.url().endsWith("/user") || response.url().endsWith("/reviews")) {
        return;
      }
      console.log(`${response.status()} ${response.url()}`);
    })
      .on('requestfailed', request =>
        console.log(`${request.failure().errorText} ${request.url()}`))

    await page.goto(ADMIN_PAGE);

    setTimeout(async () => {
      console.log("VISIT[start]: " + url)
      page.goto(url).then(
        (res) => {
          res.text().then(html => {
            // console.log("===============================================");
            // console.log(html);
            // console.log("===============================================");
          }, err => {
            console.log("===============================================");
            console.log("CONTENT ERRR");
            console.log(err);
            console.log("===============================================");
          });
          console.log('VISIT[done]')
        },
        err => { console.log('error visiting', err) }
      );
    }, 400);

    setTimeout(async () => {
        browser.close().then(cb, cb);
    }, 800);
}

app.options('/1.0/support', cors());
app.post('/1.0/support', cors(), function(req, res) {
    var url = req.body['url'] || '';
    var token = req.body['token'] || '';
    console.log("URL: ", url)

    if (true || url.length === 0) {
      if (url.length > 0) {
        let job = (cb) => adminLookup(cb, url);
        job.toString = () => url;
        q.push(job);
      }
      return sendSuccess(res, {
        message: "Thanks! An admin will take a look at it shortly!"});
    } else {
      return sendError(res, 403, "Only links from this page are allowed!");
    }

    if (!token) {
        return sendError(res, 403, "No reCAPTCHA token provided!");
    }

    fetch('https://www.google.com/recaptcha/api/siteverify', {
        method: "POST",
        body: `secret=nice-try&response=${token}`,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data['score'] > 0.3 && data['success'] === true) {
            if (/^https?:\/\/wimc\.ctf\.allesctf\.net\//.test(url) || url.length === 0) {
                if (url.length > 0) {
                    let job = (cb) => adminLookup(cb, url);
                    job.toString = () => url;
                    q.push(job);
                }
                return sendSuccess(res, {
                    message: "Thanks! An admin will take a look at it shortly!"});
            } else {
                return sendError(res, 403, "Only links from this page are allowed!");
            }
        } else {
            return sendError(res, 403, "Invalid reCAPTCHA token!");
        }
    })
});

app.listen(PORT, BIND_ADDR, () => {
    console.log(`Running on ${BIND_ADDR}:${PORT}...`);
});
