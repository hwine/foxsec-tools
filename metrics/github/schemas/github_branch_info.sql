CREATE EXTERNAL TABLE `github_branch_info`(
  `date` date COMMENT 'from deserializer', 
  `bpr_v3id` int COMMENT 'from deserializer', 
  `bpr_v4id` string COMMENT 'from deserializer', 
  `default_branch_ref` string COMMENT 'from deserializer', 
  `is_admin_enforced` boolean COMMENT 'from deserializer', 
  `name` string COMMENT 'from deserializer', 
  `name_with_owner` string COMMENT 'from deserializer', 
  `owner_v4id` string COMMENT 'from deserializer', 
  `pattern` string COMMENT 'from deserializer', 
  `prefix` string COMMENT 'from deserializer', 
  `push_actor_count` int COMMENT 'from deserializer', 
  `repo_v3id` int COMMENT 'from deserializer', 
  `repo_v4id` string COMMENT 'from deserializer', 
  `rule_conflict_count` int COMMENT 'from deserializer')
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat'
LOCATION
  's3://foxsec-metrics/github/branch_info'
TBLPROPERTIES (
  'has_encrypted_data'='false', 
  'transient_lastDdlTime'='1602114473')
