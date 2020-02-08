#!/usr/bin/env python3

"""
Script to generate checklist files via Athena queries

NOTES: 

- All queries are run in Athena's default database, so all database
  references must be fully qualified.

- The "item" column is a boolean - only true or false should be
  returned.
"""

import argparse
import botocore
import boto3
import json
import os
import os.path
import time
import sys
from datetime import date, timedelta, datetime


# Useful if we know some of the jobs are failing, eg:
#start_day = datetime(2018, 10, 31)
start_day = date.today()


def col_data_to_list(col_data):
	res = []
	for col in col_data:
		res.append(col['VarCharValue'])
	return res


def get_rra_query():
	return ("SELECT 'Risk Management' AS section, 'Must have RRA' AS item, foxsec_metrics.metadata_services.service, " +
		"'' as site, 'global' as environment, CASE WHEN foxsec_metrics.metadata_services.rradate = '' THEN False ELSE True END pass, " +
		"foxsec_metrics.metadata_services.rra as link, '' as repo " +
		"FROM foxsec_metrics.metadata_services")


def get_observatory_query():
	return ("SELECT 'Web Applications' AS section, 'A plus on Observatory' AS item, foxsec_metrics.metadata_urls.service, " +
		"foxsec_metrics.observatory.site, foxsec_metrics.metadata_urls.status AS environment, " +
		"CASE WHEN foxsec_metrics.observatory.observatory_score >= 100 THEN True ELSE False END pass, " +
		"CONCAT('https://observatory.mozilla.org/analyze/', foxsec_metrics.observatory.site) as link, '' as repo  " +
		"FROM foxsec_metrics.observatory, foxsec_metrics.metadata_urls " +
		"WHERE foxsec_metrics.observatory.site = foxsec_metrics.metadata_urls.url AND foxsec_metrics.observatory.day = '<<DAY>>' ")


def get_github_query_2fa():
	return ("""
		-- Extract Organizations 2FA status
		-- it's not a boolean, as it could be unavailable
		-- but we treat "enabled" as "pass", all else as "fail"
		WITH
		-- We only care about current status
		latestRecord AS
			(SELECT date, body.login, body.two_factor_requirement_enabled
			FROM foxsec_metrics.github_object
			JOIN
				(SELECT max(github_object.date) AS MaxDay
				FROM foxsec_metrics.github_object) md ON github_object.date = MaxDay
			-- make sure we're working with an org record
			WHERE body.has_organization_projects is not null ),
		-- From orgs we're actively monitoring
		orgsOfInterest AS
			(SELECT distinct
			"split_part"("repo", '/', 4) "Org"
			from foxsec_metrics.metadata_repos),
		-- only report once per org
		org_2fa as
			(select
			date,
			login as "Organization",
			case two_factor_requirement_enabled
			when true then true
			else false
			end as "2FA"
			from latestRecord
			JOIN orgsOfInterest ON lower(login) = lower(Org))

		SELECT distinct
			'Development' AS section,
			'Enforce 2FA' AS item,
			a.service,
			'' AS site,
			'global' AS environment,
			CONCAT('https://', a.Host, '/organizations/', a.Org, '/settings/security') AS link,
			org_2fa."2FA" AS pass,
			'' AS repo
		FROM foxsec_metrics.metadata_repo_parsed AS a
		JOIN
			org_2fa
			ON a.Org = "Organization"
		ORDER BY  (a.service)
	""")


def get_github_query_branch_protection():
	return ("SELECT 'Development' AS section, 'Enforce branch protection' AS item, service, '' as site, 'global' as environment, " +
		"CONCAT('https://github.com/', Org, '/', Repo) AS link, " +
		"every(protected) AS pass, '' as repo " +
		"FROM foxsec_metrics.default_branch_protection_status " +
		"JOIN (SELECT max(default_branch_protection_status.date) AS MaxDay " +
		"FROM foxsec_metrics.default_branch_protection_status) md ON default_branch_protection_status.date = MaxDay " +
		"GROUP BY (service, Org, Repo) " +
		"ORDER BY (service, Org, Repo)")


def get_baseline_query(section, item, column):
	return ("SELECT '" + section + "' AS section, '" + item + "' AS item, foxsec_metrics.metadata_urls.service, " +
		"foxsec_metrics.baseline_details.site, foxsec_metrics.metadata_urls.status as environment, " +
		"CASE WHEN foxsec_metrics.baseline_details.status = 'pass' THEN True ELSE False END pass, " +
		"CONCAT('https://sql.telemetry.mozilla.org/dashboard/security-baseline-service-latest?p_site_60280=', foxsec_metrics.baseline_details.site) AS link, '' as repo  " +
		"FROM foxsec_metrics.baseline_details, foxsec_metrics.metadata_urls " +
		"WHERE foxsec_metrics.baseline_details.site = foxsec_metrics.metadata_urls.url and " +
		"foxsec_metrics.baseline_details.rule = '" + column + "' and " +
		"foxsec_metrics.baseline_details.day = '<<DAY>>' ")


def get_baseline_status_query(section, item):
	return ("SELECT '" + section + "' AS section, '" + item + "' AS item, foxsec_metrics.metadata_urls.service, " +
		"foxsec_metrics.baseline_sites_latest.site, foxsec_metrics.metadata_urls.status as environment, " +
		"CASE WHEN foxsec_metrics.baseline_sites_latest.status = 'pass' THEN True ELSE False END pass, " +
		"CONCAT('https://sql.telemetry.mozilla.org/dashboard/security-baseline-service-latest?p_site_60280=', foxsec_metrics.baseline_sites_latest.site) AS link, '' as repo  " +
		"FROM foxsec_metrics.baseline_sites_latest, foxsec_metrics.metadata_urls " +
		"WHERE foxsec_metrics.baseline_sites_latest.site = foxsec_metrics.metadata_urls.url")


def run_raw_query(query):
	sys.stderr.write (query + "\n\n")
	client = boto3.client('athena', region_name='us-east-1')
	clients3 = boto3.client('s3', region_name='us-east-1')
	bucket = 'foxsec-metrics'
	tempdir = 's3://' + bucket + '/temp/'
	response = client.start_query_execution(
		QueryString=query,
		ResultConfiguration={
			'OutputLocation': tempdir,
		})

	qeid = response['QueryExecutionId']
	#print('qeid=' + qeid)
	rows_found = 0
	for x in range(0, 100):
		response = client.get_query_execution(QueryExecutionId=qeid)
		#print (response)
		state = response['QueryExecution']['Status']['State']
		#print('State=' + state)
		if state == 'RUNNING':
			time.sleep(2)
		elif state == 'SUCCEEDED':
			response = client.get_query_results(QueryExecutionId=qeid)
			#print (response)
			col_headers = []
			for row in response['ResultSet']['Rows']:
				#print('---')
				#print(row)
				if len(col_headers) == 0:
					col_headers = col_data_to_list(row['Data'])
				else :
					row_json = {}
					col_data = col_data_to_list(row['Data'])

					i = 0
					for header in col_headers:
						#print(col['VarCharValue'])
						row_json[header] = col_data[i]
						i+=1

					print(json.dumps(row_json))
					rows_found += 1

			#print ('Parsed result: ' + response['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'])
			# Delete the files
			clients3.delete_object(Bucket=bucket, Key='temp/' + qeid + '.csv')
			clients3.delete_object(Bucket=bucket, Key='temp/' + qeid + '.csv.metadata')
			break
		else:
			sys.stderr.write ('Failed - see response for details\n')
			sys.stderr.write (str(response))
			sys.stderr.write ('\n')
			break
	sys.stderr.write ("Rows returned : " + str(rows_found) + "\n\n")
	return rows_found


def run_day_query(query):
	day = start_day
	for loop in range(0, 6):
		if run_raw_query(query.replace('<<DAY>>', day.strftime("%Y-%m-%d"))) > 0:
			break
		day -= timedelta(1)


def main():
	# Risk Management
	run_raw_query(get_rra_query())

	# Infrastructure
	run_day_query(get_baseline_query('Web Applications', 'Set STS', 'rule_10035'))

	# Development
	run_raw_query(get_github_query_2fa())
	run_raw_query(get_github_query_branch_protection())

	# Web applications
	run_day_query(get_baseline_query('Web Applications', 'CSP present', 'rule_10038'))
	run_day_query(get_baseline_query('Web Applications', 'Content type', 'rule_10019'))
	run_day_query(get_baseline_query('Web Applications', 'Cookies httponly', 'rule_10010'))
	run_day_query(get_baseline_query('Web Applications', 'Cookies secure', 'rule_10011'))
	run_day_query(get_observatory_query())

	run_raw_query(get_baseline_status_query('Web Applications', 'No baseline failures'))

	# Security features
	run_day_query(get_baseline_query('Security Features', 'Anti CSRF tokens', 'rule_10202'))

	# Common issues
	run_day_query(get_baseline_query('Web Applications', 'Prevent reverse tabnabbing', 'rule_10108'))

if __name__ == '__main__':
	main()
