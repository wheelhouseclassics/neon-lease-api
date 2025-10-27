<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET");
header("Content-Type: application/json");
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 1. connect to Neon via pg_connect
$conn_str = "host=ep-cold-bar-ad3i9adr-pooler.c-2.us-east-1.aws.neon.tech
             port=5432
             dbname=neondb
             user=neondb_owner
             password=npg_rD2zXVlkZG9d
             sslmode=require";

$db = pg_connect($conn_str);

if (!$db) {
  echo json_encode(["error" => pg_last_error()]);
  exit;
}

// 2. read filters from query string
$make = $_GET['make'] ?? '';
$max_payment = $_GET['max_payment'] ?? '';

// sanitize-ish
$make = trim($make);
$max_payment = trim($max_payment);

// 3. build base SQL & params safely
$sql = "SELECT make, model, year, payment
        FROM lease_programs
        WHERE 1=1";
$params = [];
$idx = 1;

// filter: make
if ($make !== '') {
  $sql .= " AND make ILIKE $" . $idx;
  $params[] = $make;
  $idx++;
}

// filter: max payment
if ($max_payment !== '') {
  $sql .= " AND payment <= $" . $idx;
  $params[] = $max_payment;
  $idx++;
}

// sort best (cheapest payment first)
$sql .= " ORDER BY payment::numeric ASC LIMIT 50;";

// 4. run query
$result = pg_query_params($db, $sql, $params);

if (!$result) {
  echo json_encode(["error" => pg_last_error($db)]);
  exit;
}

$rows = pg_fetch_all($result) ?: [];
pg_close($db);

// 5. respond
echo json_encode([
  "records" => $rows
], JSON_PRETTY_PRINT);
