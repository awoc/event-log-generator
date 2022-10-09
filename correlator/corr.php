<?php
include_once "functions.php";

if (!isset($_REQUEST["value"])) {
  throw new Exception("file parameter is missing");
}

$requested_message = $_REQUEST["value"];

$dir = "./messages/";
if ($dh = opendir($dir)) {
  while (($file = readdir($dh)) !== false) {
    $prefix = substr($file, 0, 1);
    if ($prefix != ".") {
      $message = json_decode(file_get_contents($dir . $file), true);
      $message_file = $message["file"];

      if ($requested_message === $message_file) {
        $xml = getMessageTemplate($message_file);
        header("Content-type: application/xml");
        print_r($xml->asXML());
        unlink($dir . $file);
        exit();
      }
    }
  }
  closedir($dh);
}

$headers = apache_request_headers();
$tmpfname = tempnam("./correlate", "");
$current = file_put_contents(
  $tmpfname,
  json_encode([$_REQUEST, $headers], JSON_PRETTY_PRINT)
);

header("Cpee-Callback: true");
exit();
