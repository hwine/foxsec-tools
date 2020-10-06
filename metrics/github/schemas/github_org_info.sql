CREATE EXTERNAL TABLE `github_org_info`(
  `login` string COMMENT 'from deserializer', 
  `name` string COMMENT 'from deserializer', 
  `org_v3id` int COMMENT 'from deserializer', 
  `org_v4id` string COMMENT 'from deserializer', 
  `requires_two_factor_authentication` boolean COMMENT 'from deserializer')
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat'
LOCATION
  's3://foxsec-metrics/github/org_info'
TBLPROPERTIES (
  'has_encrypted_data'='false', 
  'transient_lastDdlTime'='1602024341')
