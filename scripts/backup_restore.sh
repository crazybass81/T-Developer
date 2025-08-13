#!/bin/bash

# T-Developer Evolution System - Backup and Restore Strategy
# Comprehensive backup solution for RDS, DynamoDB, and S3

set -e

# Configuration
ENVIRONMENT=${1:-development}
OPERATION=${2:-backup}  # backup or restore
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_BUCKET="t-developer-backups-${ENVIRONMENT}"
AWS_REGION=${AWS_REGION:-us-east-1}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed"
    fi

    # Check PostgreSQL client
    if ! command -v pg_dump &> /dev/null; then
        warning "pg_dump not found - RDS backup will use snapshots only"
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured"
    fi

    log "Prerequisites check completed"
}

# Get RDS instance identifier
get_rds_instance() {
    aws rds describe-db-instances \
        --region ${AWS_REGION} \
        --query "DBInstances[?contains(DBInstanceIdentifier, 't-developer') && contains(DBInstanceIdentifier, '${ENVIRONMENT}')].DBInstanceIdentifier" \
        --output text | head -1
}

# Get DynamoDB tables
get_dynamodb_tables() {
    aws dynamodb list-tables \
        --region ${AWS_REGION} \
        --query "TableNames[?contains(@, 't-developer') && contains(@, '${ENVIRONMENT}')]" \
        --output text
}

# Backup RDS
backup_rds() {
    local db_instance=$(get_rds_instance)

    if [ -z "$db_instance" ]; then
        warning "No RDS instance found for environment: ${ENVIRONMENT}"
        return
    fi

    log "Backing up RDS instance: ${db_instance}"

    # Create manual snapshot
    local snapshot_id="t-developer-manual-${ENVIRONMENT}-${TIMESTAMP}"

    aws rds create-db-snapshot \
        --db-instance-identifier ${db_instance} \
        --db-snapshot-identifier ${snapshot_id} \
        --region ${AWS_REGION} \
        --tags "Key=Environment,Value=${ENVIRONMENT}" \
               "Key=Type,Value=Manual" \
               "Key=Timestamp,Value=${TIMESTAMP}"

    log "RDS snapshot created: ${snapshot_id}"

    # Wait for snapshot to complete
    log "Waiting for snapshot to complete..."
    aws rds wait db-snapshot-completed \
        --db-snapshot-identifier ${snapshot_id} \
        --region ${AWS_REGION}

    log "RDS backup completed successfully"

    # Export snapshot metadata
    aws rds describe-db-snapshots \
        --db-snapshot-identifier ${snapshot_id} \
        --region ${AWS_REGION} \
        > "/tmp/rds_snapshot_${TIMESTAMP}.json"

    # Upload metadata to S3
    aws s3 cp "/tmp/rds_snapshot_${TIMESTAMP}.json" \
        "s3://${BACKUP_BUCKET}/rds/metadata/${TIMESTAMP}.json"
}

# Backup DynamoDB
backup_dynamodb() {
    local tables=$(get_dynamodb_tables)

    if [ -z "$tables" ]; then
        warning "No DynamoDB tables found for environment: ${ENVIRONMENT}"
        return
    fi

    log "Backing up DynamoDB tables..."

    for table in $tables; do
        log "Backing up table: ${table}"

        # Create on-demand backup
        local backup_name="${table}-backup-${TIMESTAMP}"

        aws dynamodb create-backup \
            --table-name ${table} \
            --backup-name ${backup_name} \
            --region ${AWS_REGION}

        # Export table to S3 (for long-term storage)
        aws dynamodb export-table-to-point-in-time \
            --table-arn "arn:aws:dynamodb:${AWS_REGION}:$(aws sts get-caller-identity --query Account --output text):table/${table}" \
            --s3-bucket ${BACKUP_BUCKET} \
            --s3-prefix "dynamodb/${table}/${TIMESTAMP}" \
            --export-format DYNAMODB_JSON \
            --region ${AWS_REGION} || warning "Table export not available for ${table}"

        log "DynamoDB table ${table} backup initiated"
    done

    log "DynamoDB backup completed"
}

# Backup S3 buckets
backup_s3() {
    log "Backing up S3 buckets..."

    # List Evolution System buckets
    local buckets=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, 't-developer') && contains(Name, '${ENVIRONMENT}')].Name" \
        --output text)

    for bucket in $buckets; do
        if [[ "$bucket" != *"backup"* ]]; then
            log "Syncing bucket: ${bucket}"

            # Sync to backup bucket
            aws s3 sync "s3://${bucket}" \
                "s3://${BACKUP_BUCKET}/s3-backups/${bucket}/${TIMESTAMP}/" \
                --delete \
                --region ${AWS_REGION}

            # Create bucket inventory
            aws s3api put-bucket-inventory-configuration \
                --bucket ${bucket} \
                --id "backup-inventory-${TIMESTAMP}" \
                --inventory-configuration \
                "Destination={S3BucketDestination={Bucket=arn:aws:s3:::${BACKUP_BUCKET},Prefix=inventory/${bucket}/,Format=CSV}},IsEnabled=true,Id=backup-inventory-${TIMESTAMP},IncludedObjectVersions=Current,Schedule={Frequency=Daily}" \
                --region ${AWS_REGION} || true
        fi
    done

    log "S3 backup completed"
}

# Backup ElastiCache
backup_elasticache() {
    log "Backing up ElastiCache..."

    # Get replication group
    local replication_group=$(aws elasticache describe-replication-groups \
        --region ${AWS_REGION} \
        --query "ReplicationGroups[?contains(ReplicationGroupId, 't-developer') && contains(ReplicationGroupId, '${ENVIRONMENT}')].ReplicationGroupId" \
        --output text | head -1)

    if [ -z "$replication_group" ]; then
        warning "No ElastiCache replication group found"
        return
    fi

    # Create manual snapshot
    local snapshot_name="t-developer-cache-backup-${ENVIRONMENT}-${TIMESTAMP}"

    aws elasticache create-snapshot \
        --replication-group-id ${replication_group} \
        --snapshot-name ${snapshot_name} \
        --region ${AWS_REGION}

    log "ElastiCache snapshot created: ${snapshot_name}"
}

# Backup secrets and parameters
backup_secrets() {
    log "Backing up secrets and parameters..."

    # Backup Secrets Manager secrets
    local secrets=$(aws secretsmanager list-secrets \
        --region ${AWS_REGION} \
        --query "SecretList[?contains(Name, 't-developer') && contains(Name, '${ENVIRONMENT}')].Name" \
        --output text)

    mkdir -p "/tmp/secrets_backup_${TIMESTAMP}"

    for secret in $secrets; do
        log "Backing up secret: ${secret}"

        # Get secret metadata (not the actual value for security)
        aws secretsmanager describe-secret \
            --secret-id ${secret} \
            --region ${AWS_REGION} \
            > "/tmp/secrets_backup_${TIMESTAMP}/${secret//\//_}.json"
    done

    # Backup Parameter Store parameters
    aws ssm get-parameters-by-path \
        --path "/t-developer/${ENVIRONMENT}" \
        --recursive \
        --with-decryption \
        --region ${AWS_REGION} \
        > "/tmp/secrets_backup_${TIMESTAMP}/parameters.json"

    # Create encrypted archive
    tar czf "/tmp/secrets_backup_${TIMESTAMP}.tar.gz" \
        -C "/tmp" "secrets_backup_${TIMESTAMP}"

    # Encrypt with KMS before uploading
    aws kms encrypt \
        --key-id "alias/t-developer-backup-${ENVIRONMENT}" \
        --plaintext "fileb:///tmp/secrets_backup_${TIMESTAMP}.tar.gz" \
        --output text \
        --query CiphertextBlob \
        --region ${AWS_REGION} | base64 -d > "/tmp/secrets_backup_${TIMESTAMP}.encrypted"

    # Upload to S3
    aws s3 cp "/tmp/secrets_backup_${TIMESTAMP}.encrypted" \
        "s3://${BACKUP_BUCKET}/secrets/${TIMESTAMP}.encrypted" \
        --server-side-encryption aws:kms \
        --ssekms-key-id "alias/t-developer-backup-${ENVIRONMENT}"

    # Cleanup
    rm -rf "/tmp/secrets_backup_${TIMESTAMP}"*

    log "Secrets backup completed"
}

# Create backup manifest
create_backup_manifest() {
    log "Creating backup manifest..."

    cat > "/tmp/backup_manifest_${TIMESTAMP}.json" <<EOF
{
    "timestamp": "${TIMESTAMP}",
    "environment": "${ENVIRONMENT}",
    "components": {
        "rds": "$(get_rds_instance)",
        "dynamodb_tables": [$(get_dynamodb_tables | tr '\t' ',' | sed 's/,/","/g' | sed 's/^/"/;s/$/"/')]
    },
    "backup_location": "s3://${BACKUP_BUCKET}",
    "created_by": "$(aws sts get-caller-identity --query Arn --output text)",
    "region": "${AWS_REGION}"
}
EOF

    # Upload manifest
    aws s3 cp "/tmp/backup_manifest_${TIMESTAMP}.json" \
        "s3://${BACKUP_BUCKET}/manifests/${TIMESTAMP}.json"

    log "Backup manifest created"
}

# Restore RDS from snapshot
restore_rds() {
    local snapshot_id=$1

    if [ -z "$snapshot_id" ]; then
        error "Snapshot ID required for restore"
    fi

    log "Restoring RDS from snapshot: ${snapshot_id}"

    # Generate new instance identifier
    local new_instance="t-developer-restored-${ENVIRONMENT}-${TIMESTAMP}"

    aws rds restore-db-instance-from-db-snapshot \
        --db-instance-identifier ${new_instance} \
        --db-snapshot-identifier ${snapshot_id} \
        --region ${AWS_REGION}

    log "RDS restore initiated: ${new_instance}"

    # Wait for instance to be available
    aws rds wait db-instance-available \
        --db-instance-identifier ${new_instance} \
        --region ${AWS_REGION}

    log "RDS restore completed: ${new_instance}"
}

# Main backup function
perform_backup() {
    log "Starting backup for environment: ${ENVIRONMENT}"

    # Create backup bucket if not exists
    aws s3api create-bucket \
        --bucket ${BACKUP_BUCKET} \
        --region ${AWS_REGION} \
        --create-bucket-configuration LocationConstraint=${AWS_REGION} 2>/dev/null || true

    # Enable versioning on backup bucket
    aws s3api put-bucket-versioning \
        --bucket ${BACKUP_BUCKET} \
        --versioning-configuration Status=Enabled

    # Run backups
    backup_rds
    backup_dynamodb
    backup_s3
    backup_elasticache
    backup_secrets
    create_backup_manifest

    log "==================================="
    log "Backup completed successfully!"
    log "Timestamp: ${TIMESTAMP}"
    log "Location: s3://${BACKUP_BUCKET}"
    log "==================================="
}

# Main restore function
perform_restore() {
    local backup_timestamp=$3

    if [ -z "$backup_timestamp" ]; then
        error "Backup timestamp required for restore"
    fi

    log "Starting restore from backup: ${backup_timestamp}"

    # Download and verify manifest
    aws s3 cp "s3://${BACKUP_BUCKET}/manifests/${backup_timestamp}.json" \
        "/tmp/restore_manifest.json"

    # Parse manifest and restore components
    # This is a simplified example - implement based on your needs

    warning "Restore functionality needs to be customized for your specific requirements"

    log "Restore process initiated"
}

# Cleanup old backups
cleanup_old_backups() {
    local retention_days=${1:-30}

    log "Cleaning up backups older than ${retention_days} days..."

    # Calculate cutoff date
    local cutoff_date=$(date -d "${retention_days} days ago" +%Y-%m-%d)

    # List and delete old RDS snapshots
    aws rds describe-db-snapshots \
        --region ${AWS_REGION} \
        --query "DBSnapshots[?SnapshotType=='manual' && contains(DBSnapshotIdentifier, 't-developer-manual-${ENVIRONMENT}')].{ID:DBSnapshotIdentifier,Created:SnapshotCreateTime}" \
        --output json | jq -r ".[] | select(.Created < \"${cutoff_date}\") | .ID" | \
    while read snapshot_id; do
        log "Deleting old RDS snapshot: ${snapshot_id}"
        aws rds delete-db-snapshot \
            --db-snapshot-identifier ${snapshot_id} \
            --region ${AWS_REGION}
    done

    log "Cleanup completed"
}

# Main execution
main() {
    check_prerequisites

    case ${OPERATION} in
        backup)
            perform_backup
            ;;
        restore)
            perform_restore "$@"
            ;;
        cleanup)
            cleanup_old_backups ${3:-30}
            ;;
        *)
            error "Invalid operation: ${OPERATION}. Use 'backup', 'restore', or 'cleanup'"
            ;;
    esac
}

# Run main function
main "$@"
