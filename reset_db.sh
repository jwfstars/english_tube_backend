#!/bin/bash
# English Tube Backend - 清空数据库脚本

export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
export PGPASSWORD="your_password_here"

echo "清空数据库..."
psql -h localhost -U english_tube -d english_tube -c "TRUNCATE videos, subtitles, word_cards, phrase_cards CASCADE;"

echo ""
echo "验证:"
psql -h localhost -U english_tube -d english_tube -c "SELECT 'videos' as t, count(*) FROM videos UNION ALL SELECT 'subtitles', count(*) FROM subtitles UNION ALL SELECT 'word_cards', count(*) FROM word_cards UNION ALL SELECT 'phrase_cards', count(*) FROM phrase_cards;"
