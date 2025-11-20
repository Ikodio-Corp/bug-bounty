#!/bin/bash

set -e

CDN_PROVIDER=${1:-cloudflare}
DOMAIN=${2:-ikodio.com}

echo "CDN Setup for IKODIO BugBounty"
echo "Provider: $CDN_PROVIDER"
echo "Domain: $DOMAIN"
echo ""

if [ "$CDN_PROVIDER" == "cloudflare" ]; then
    echo "Setting up Cloudflare CDN..."
    
    if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
        echo "Error: CLOUDFLARE_API_TOKEN environment variable not set"
        exit 1
    fi
    
    ZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=${DOMAIN}" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" | jq -r '.result[0].id')
    
    if [ -z "$ZONE_ID" ] || [ "$ZONE_ID" == "null" ]; then
        echo "Error: Could not find zone for domain ${DOMAIN}"
        exit 1
    fi
    
    echo "Zone ID: $ZONE_ID"
    
    echo "Enabling CDN caching..."
    curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/cache_level" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{"value":"aggressive"}' | jq .
    
    echo "Enabling Brotli compression..."
    curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/brotli" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{"value":"on"}' | jq .
    
    echo "Enabling Auto Minify..."
    curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/minify" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{"value":{"css":"on","html":"on","js":"on"}}' | jq .
    
    echo "Setting Browser Cache TTL..."
    curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/browser_cache_ttl" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{"value":31536000}' | jq .
    
    echo "Creating Page Rules..."
    
    echo "Rule 1: Cache everything for static assets"
    curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/pagerules" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
          "targets": [
            {
              "target": "url",
              "constraint": {
                "operator": "matches",
                "value": "*'${DOMAIN}'/_next/static/*"
              }
            }
          ],
          "actions": [
            {"id": "cache_level", "value": "cache_everything"},
            {"id": "edge_cache_ttl", "value": 31536000}
          ],
          "priority": 1,
          "status": "active"
        }' | jq .
    
    echo "Rule 2: Cache images"
    curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/pagerules" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
          "targets": [
            {
              "target": "url",
              "constraint": {
                "operator": "matches",
                "value": "*'${DOMAIN}'/images/*"
              }
            }
          ],
          "actions": [
            {"id": "cache_level", "value": "cache_everything"},
            {"id": "edge_cache_ttl", "value": 2592000}
          ],
          "priority": 2,
          "status": "active"
        }' | jq .
    
    echo "Rule 3: Bypass cache for API"
    curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/pagerules" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
          "targets": [
            {
              "target": "url",
              "constraint": {
                "operator": "matches",
                "value": "api.'${DOMAIN}'/*"
              }
            }
          ],
          "actions": [
            {"id": "cache_level", "value": "bypass"}
          ],
          "priority": 3,
          "status": "active"
        }' | jq .
    
    echo ""
    echo "Cloudflare CDN setup completed"
    
elif [ "$CDN_PROVIDER" == "cloudfront" ]; then
    echo "Setting up AWS CloudFront CDN..."
    
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        echo "Error: AWS credentials not set"
        exit 1
    fi
    
    S3_BUCKET="ikodio-static-assets"
    
    echo "Creating S3 bucket for static assets..."
    aws s3 mb s3://${S3_BUCKET} --region us-east-1 || true
    
    echo "Configuring S3 bucket for website hosting..."
    aws s3 website s3://${S3_BUCKET} \
        --index-document index.html \
        --error-document error.html
    
    echo "Setting bucket policy..."
    cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${S3_BUCKET}/*"
    }
  ]
}
EOF
    
    aws s3api put-bucket-policy \
        --bucket ${S3_BUCKET} \
        --policy file://bucket-policy.json
    
    rm bucket-policy.json
    
    echo "Creating CloudFront distribution..."
    cat > cloudfront-config.json << EOF
{
  "CallerReference": "ikodio-$(date +%s)",
  "Comment": "IKODIO BugBounty CDN",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-${S3_BUCKET}",
        "DomainName": "${S3_BUCKET}.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-${S3_BUCKET}",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "Compress": true,
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    }
  },
  "Aliases": {
    "Quantity": 1,
    "Items": ["cdn.${DOMAIN}"]
  },
  "PriceClass": "PriceClass_All"
}
EOF
    
    DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config file://cloudfront-config.json \
        --query 'Distribution.Id' \
        --output text)
    
    rm cloudfront-config.json
    
    echo "Distribution ID: $DISTRIBUTION_ID"
    echo "Distribution Domain: $(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query 'Distribution.DomainName' --output text)"
    
    echo ""
    echo "CloudFront CDN setup completed"
    echo "Update DNS to point cdn.${DOMAIN} to the CloudFront domain"
    
else
    echo "Error: Unsupported CDN provider: $CDN_PROVIDER"
    echo "Supported providers: cloudflare, cloudfront"
    exit 1
fi

echo ""
echo "CDN setup completed successfully"
