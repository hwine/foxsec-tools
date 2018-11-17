# Wrapper for running the main github transformer

set -eux
# Install other tools

# Install python tools we need
pip3 install --upgrade \
  awscli \

# we need the heroku cli - this is recommended docker install
# per https://devcenter.heroku.com/articles/heroku-cli
curl https://cli-assets.heroku.com/install.sh | sh

# create credential files assume env variables set
cat >~/.netrc <<EOF
machine api.heroku.com
  login $HEROKU_USER
  password $HEROKU_API_KEY
machine git.heroku.com
  login $HEROKU_USER
  password $HEROKU_API_KEY
EOF
mkdir ~/.aws
cat > ~/.aws/credentials <<DELIM
[default]
aws_access_key_id = $AWS_ACCESS_KEY
aws_secret_access_key = $AWS_SECRET_KEY
DELIM

today=$(date --utc --iso)

# create local structure
mkdir -p s3bucket/{raw,members_json}
rawFile=s3bucket/raw/${today}-members.json
dbFile=s3bucket/members_json/${today}-members.json

# collect data
heroku members --json --team mozillacorporation >$rawFile

# transform:
#   - add date field
#   - reformat to one object per line
jq -erc ".[] | . + { \"date\": \"$today\" } " \
  < $rawFile >$dbFile

# Write all files to aws
aws s3 sync s3bucket/ s3://foxsec-metrics/heroku/

