#!/bin/bash
set -e

echo "⏳ Aguardando banco de dados ficar pronto..."
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import settings

async def wait_for_db():
    engine = create_async_engine(settings.database_url)
    for i in range(30):
        try:
            async with engine.connect() as conn:
                await conn.execute(text('SELECT 1'))
            print('✅ Banco de dados pronto!')
            return
        except Exception as e:
            print(f'⏳ Tentativa {i+1}/30 - banco ainda não disponível...')
            await asyncio.sleep(2)
    raise Exception('❌ Banco de dados não ficou pronto após 30 tentativas')

asyncio.run(wait_for_db())
"

echo "🔄 Rodando migrations..."
alembic upgrade head
echo "✅ Migrations concluídas!"

echo "🚀 Iniciando servidor..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 "$@"
