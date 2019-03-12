CREATE EXTERNAL TABLE IF NOT EXISTS foxsec_metrics.metadata (
  "audits" array<struct<
      auditor:string,
      date:string,
      NC_link:string,
      status:string,
      tracker:string>>,
  "bugzilla" array<struct<
      component:string,
      product:string>>,
  "checklists" array<string>,
  "codeRepositories" array<struct<
      branchesToProtect:array<string>,
      NC_comment:string,
      hostingService:string,
      status:string,
      url:string,
      vcs:string>>,
  "contact" string,
  "dockerImageURLs" array<string>,
  "hostingProvider" array<struct<
      env:string,
      id:string,
      NC_type:string>>,
  "notes" string,
  "riskSummary" string,
  "rra" string,
  "rraData" string,
  "rraDate" string,
  "rraImpact" string,
  "security" string,
  "seeAlso" array<string>,
  "service" string,
  "serviceKey" string,
  "sites" array<struct<
      category:string,
      NC_comment:string,
      riskSummary:string,
      rra:string,
      site:string,
      urls:array<struct<
          baselineScanConf:string,
          NC_comment:string,
          exceptions:array<string>,
          NC_path:string,
          qualifier:string,
          special:string,
          status:string,
          url:string>>>>,
  "sourceControl" array<string>,
  "version" int>
)
ROW FORMAT SERDE 
  'org.apache.hive.hcatalog.data.JsonSerDe' 
WITH SERDEPROPERTIES (
  'ignore.malformed.json'='true',
)
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://foxsec-metrics/metadata/metadata_json/'
TBLPROPERTIES ('has_encrypted_data'='false');
