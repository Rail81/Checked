#!/bin/bash

# Проверяем, что переданы параметры
if [ $# -ne 2 ]; then
    echo "Usage: $0 <database_backup_file> <uploads_backup_file>"
    exit 1
fi

DB_BACKUP=$1
UPLOADS_BACKUP=$2
DB_NAME="doc_management"
DB_USER="doc_user"

# Проверяем существование файлов
if [ ! -f "$DB_BACKUP" ]; then
    echo "Database backup file not found: $DB_BACKUP"
    exit 1
fi

if [ ! -f "$UPLOADS_BACKUP" ]; then
    echo "Uploads backup file not found: $UPLOADS_BACKUP"
    exit 1
fi

# Останавливаем сервисы
systemctl stop docmanagement
systemctl stop docmanagement-bot

# Восстанавливаем базу данных
psql -U $DB_USER -d $DB_NAME < $DB_BACKUP

# Восстанавливаем файлы
tar -xzf $UPLOADS_BACKUP -C /

# Запускаем сервисы
systemctl start docmanagement
systemctl start docmanagement-bot

echo "Restore completed successfully!"
