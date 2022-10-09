<?php
function getMessageTemplate($file)
{
  $file = "./message-templates/" . $file;
  $content = simplexml_load_file($file);

  if ($content == false) {
    throw new Exception("file not found");
  }

  return $content;
}
