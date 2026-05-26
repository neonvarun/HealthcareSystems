-- Create dedicated Odoo database user (Odoo 19.0 refuses to use 'postgres' superuser)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'odoo') THEN
    CREATE ROLE odoo WITH LOGIN PASSWORD 'odoo';
    ALTER ROLE odoo CREATEDB;
  END IF;
END
$$;
