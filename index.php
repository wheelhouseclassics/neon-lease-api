<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

// --- Connect to Neon ---
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

// --- Read filters from URL ---
$make = $_GET['make'] ?? '';
$max_payment = $_GET['max_payment'] ?? '';

// --- Build query safely ---
$sql = "SELECT make, model, year, payment, due_at_signing, msrp, deal_index
        FROM lease_programs
        WHERE deal_index IS NOT NULL";
$params = [];
$idx = 1;

if ($make !== '') {
  $sql .= " AND make ILIKE $" . $idx;
  $params[] = "%" . $make . "%";
  $idx++;
}

if ($max_payment !== '') {
  $sql .= " AND payment::numeric <= $" . $idx;
  $params[] = $max_payment;
  $idx++;
}

// --- Final sort + limit ---
$sql .= " ORDER BY deal_index ASC LIMIT 200;";

// --- Run query ---
if (!empty($params)) {
  $result = pg_query_params($db, $sql, $params);
} else {
  $result = pg_query($db, $sql);
}

if (!$result) {
  echo json_encode(["error" => pg_last_error($db)]);
  exit;
}

$rows = pg_fetch_all($result) ?: [];
pg_close($db);

// --- Output ---
echo json_encode(["records" => $rows], JSON_PRETTY_PRINT);
?>
