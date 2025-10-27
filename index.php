<?php
header("Content-Type: application/json");
error_reporting(E_ALL);
ini_set('display_errors', 1);

$conn_str = "host=ep-cold-bar-ad3i9adr-pooler.c-2.us-east-1.aws.neon.tech
             port=5432
             dbname=neondb
             user=neondb_owner
             password=npg_rD2zXVlkZG9d
             sslmode=require";

$conn = pg_connect($conn_str);

if (!$conn) {
  echo json_encode(["error" => pg_last_error()]);
  exit;
}

$result = pg_query($conn, "SELECT make, model, year, payment FROM lease_programs LIMIT 10;");
if (!$result) {
  echo json_encode(["error" => pg_last_error()]);
  exit;
}

$rows = pg_fetch_all($result);
pg_close($conn);

echo json_encode(["records" => $rows], JSON_PRETTY_PRINT);
?>
