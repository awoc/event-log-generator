<?php
include_once "functions.php";

if (!isset($_REQUEST["file"])) {
  throw new Exception("file parameter is missing");
}

// Check if multiple parameters are passed
if (gettype($_REQUEST["file"]) === "array") {
  // Request mesg.php/file[]=value1&file[]=value2
  $sent_files = $_REQUEST["file"];
} else {
  // Request mesg.php/file=value1
  // OR list mesg.php/file=value1,value2,value3
  $split_files = explode(",", $_REQUEST["file"]);
  $sent_files = [];
  foreach ($split_files as $file) {
    array_push($sent_files, $file);
  }
}

$dir = "./correlate/";
if ($dh = opendir($dir)) {
  while (($file = readdir($dh)) !== false) {
    $prefix = substr($file, 0, 1);
    if ($prefix != ".") {
      json_decode(file_get_contents($dir . $file));
      $corr = json_decode(file_get_contents($dir . $file), true);

      $requested_msg = $corr[0]["value"];
      $search_result = array_search($requested_msg, $sent_files);

      if ($search_result !== false) {
        $callback = $corr[1]["Cpee-Callback"];

        if ($callback === null) {
          throw new Exception("Missing Cpee-Callback");
        }

        $sent_file = $sent_files[$search_result];
        $xml = getMessageTemplate($sent_file);

        $opts = [
          "http" => [
            "method" => "PUT",
            "header" => "Content-type: application/xml",
            "content" => $xml,
          ],
        ];
        $context = stream_context_create($opts);
        $result = file_get_contents($callback, false, $context);
        unlink($dir . $file);
        exit();
      }
    }
  }
  closedir($dh);
}

foreach ($sent_files as $file) {
  $jsonObj = new stdClass();
  $jsonObj->file = $file;

  $tmpfname = tempnam("./messages", "");
  $current = file_put_contents(
    $tmpfname,
    json_encode($jsonObj, JSON_PRETTY_PRINT)
  );
}

exit();
