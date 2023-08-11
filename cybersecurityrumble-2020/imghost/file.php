<?php

session_start();

$filename = substr($_SERVER["DOCUMENT_URI"], 3);

if(!file_exists("/dev/shm/uploads/" . $filename) || strlen($filename) > 24) die("<h1>404 File not found</h1>");

if($_GET["report"] == "1") {
	if(!file_exists("/dev/shm/reports")) mkdir("/dev/shm/reports");
	if(!file_exists("/dev/shm/reports/" . $filename)) {
		file_put_contents("/dev/shm/reports/" . $filename, "");
	}
	die("File has been reported, thanks for your help!");
}

header("Content-Security-Policy: script-src 'none';");

echo '<object border="2px" data="/uploads/' . $filename . '?lang=en&ref=website&pd=' . md5(session_id()) . '&u=' . uniqid() . '&client=' . session_id() . '&method=direct&t=' . time() . '"></object>';
echo '<br/><a href="?report=1">Report abuse</a>';

?>
