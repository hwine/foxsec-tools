# Heroku data collection

Current interest is in ensuring that all accounts have appropriate
controls. As such, only the Heroku 'members' data is needed.

That information is available directly from the ``heroku`` cli tool, in
JSON format. The data needs reformatting to be Athena compliant. The
tables described here work on the transformed data.
