<?php
header("Content-Type: application/json");
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 1. Your Neon API key
$api_key = "napi_tdic91bhx55200pko5ukwpb09qntqz5vzzk56cnzv23913o6j9elfyqsxqusnlyr";

// 2. The SQL you want Neon to run
$sql = "SELECT make, model, year, payment FROM lease_programs LIMIT 10;";
$body = json_encode(["sql" => $sql]);

// 3. Your Neon project + branch (from your dashboard URL)
// Using data-api.neon.tech instead of console.neon.tech
$url = "https://data-api.neon.tech/v2/projects/bitter-scene-77398435/branches/br-red-sea-adw4083a/query";

// 4. Init curl
$ch = curl_init($url);

// 5. Force DNS resolution for data-api.neon.tech so Render stops crying about lookup
// If this IP ever changes, you’ll have to update it, but it unblocks you right now.
curl_setopt($ch, CURLOPT_RESOLVE, [
  "data-api.neon.tech:443:18.215.141.236"
]);

// 6. Set the rest of the curl options
curl_setopt_array($ch, [
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_HTTPHEADER => [
    "Authorization: Bearer $api_key",
    "Content-Type: application/json"
  ],
  CURLOPT_POST => true,
  CURLOPT_POSTFIELDS => $body,
  CURLOPT_TIMEOUT => 10,
]);

// 7. Execute
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$err = curl_error($ch);
curl_close($ch);

// 8. Handle errors or return data
if ($err) {
  echo json_encode([
    "error" => $err,
    "http_status" => $http_code
  ], JSON_PRETTY_PRINT);
  exit;
}

echo json_encode([
  "http_status" => $http_code,
  "response" => json_decode($response, true)
], JSON_PRETTY_PRINT);
?>
