#!/bin/bash

# Настройки
BACKUP_DIR="/path/to/backups"
DB_NAME="doc_management"
DB_USER="doc_user"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Создаем директорию для бэкапов если её нет
mkdir -p $BACKUP_DIR

# Бэкап базы данных
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Бэкап загруженных файлов
tar -czf $BACKUP_DIR/uploads_backup_$TIMESTAMP.tar.gz /path/to/document-management-system/uploads/

# Удаляем старые бэкапы (оставляем только за последние 7 дней)
find $BACKUP_DIR -name "db_backup_*" -mtime +7 -delete
find $BACKUP_DIR -name "uploads_backup_*" -mtime +7 -delete
