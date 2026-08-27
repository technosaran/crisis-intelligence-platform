@echo off
echo Generating Alembic Migrations...
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
cd ..
echo Done!
