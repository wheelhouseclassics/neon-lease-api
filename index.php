<?php
header("Content-Type: application/json");
error_reporting(E_ALL);
ini_set('display_errors', 1);

$api_key = "napi_tdic91bhx55200pko5ukwpb09qntqz5vzzk56cnzv23913o6j9elfyqsxqusnlyr";

$sql = "SELECT make, model, year, payment FROM lease_programs LIMIT 10;";
$body = json_encode(["sql" => $sql]);

$url = "https://data-api.neon.tech/v2/projects/bitter-scene-77398435/branches/br-red-sea-adw4083a/query";

$ch = curl_init($url);
curl_setopt_array($ch, [
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_HTTPHEADER => [
    "Authorization: Bearer $api_key",
    "Content-Type: application/json"
  ],
  CURLOPT_POST => true,
  CURLOPT_POSTFIELDS => $body,
  CURLOPT_TIMEOUT => 20,
  CURLOPT_IPRESOLVE => CURL_IPRESOLVE_V4,
  CURLOPT_SSL_VERIFYPEER => true,
  CURLOPT_SSL_VERIFYHOST => 2,
  CURLOPT_VERBOSE => true
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$err = curl_error($ch);
curl_close($ch);

if ($err) {
  echo json_encode(["error" => $err, "http_status" => $http_code]);
  exit;
}

echo json_encode(["http_status" => $http_code, "response" => json_decode($response, true)], JSON_PRETTY_PRINT);
?>
