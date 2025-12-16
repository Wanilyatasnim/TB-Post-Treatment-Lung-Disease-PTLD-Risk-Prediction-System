# Generated migration to enable Row Level Security (RLS) on all tables
# This provides defense-in-depth security for Supabase

from django.db import migrations


def enable_rls(apps, schema_editor):
    """
    Enable RLS on all tables and create policies that allow Django's postgres user
    to access everything (since Django handles authentication/authorization).
    """
    # Only run on PostgreSQL (Supabase), not SQLite
    if schema_editor.connection.vendor != 'postgresql':
        return
        
    with schema_editor.connection.cursor() as cursor:
        # List of all tables that need RLS
        tables = [
            'accounts_user',
            'accounts_user_groups',
            'accounts_user_user_permissions',
            'auth_group',
            'auth_group_permissions',
            'auth_permission',
            'authtoken_token',
            'clinical_auditlog',
            'clinical_monitoringvisit',
            'clinical_patient',
            'clinical_riskprediction',
            'clinical_treatmentmodification',
            'clinical_treatmentregimen',
            'django_admin_log',
            'django_content_type',
            'django_migrations',
            'django_session',
        ]
        
        for table in tables:
            # Enable RLS on the table
            cursor.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY;')
            
            # Create a policy that allows the postgres user (Django's connection user) 
            # to perform all operations. Django handles authentication/authorization.
            # This prevents PostgREST from accessing data without proper authentication.
            cursor.execute(f'''
                CREATE POLICY "Allow Django postgres user full access" ON "{table}"
                FOR ALL
                TO postgres
                USING (true)
                WITH CHECK (true);
            ''')
            
            # Optionally, you can create a policy for authenticated Supabase users
            # if you plan to use PostgREST in the future:
            # cursor.execute(f'''
            #     CREATE POLICY "Allow authenticated Supabase users" ON "{table}"
            #     FOR SELECT
            #     TO authenticated
            #     USING (true);
            # ''')


def disable_rls(apps, schema_editor):
    """Disable RLS and drop policies (reverse migration)"""
    # Only run on PostgreSQL (Supabase), not SQLite
    if schema_editor.connection.vendor != 'postgresql':
        return
        
    with schema_editor.connection.cursor() as cursor:
        tables = [
            'accounts_user',
            'accounts_user_groups',
            'accounts_user_user_permissions',
            'auth_group',
            'auth_group_permissions',
            'auth_permission',
            'authtoken_token',
            'clinical_auditlog',
            'clinical_monitoringvisit',
            'clinical_patient',
            'clinical_riskprediction',
            'clinical_treatmentmodification',
            'clinical_treatmentregimen',
            'django_admin_log',
            'django_content_type',
            'django_migrations',
            'django_session',
        ]
        
        for table in tables:
            # Drop policies
            cursor.execute(f'DROP POLICY IF EXISTS "Allow Django postgres user full access" ON "{table}";')
            # Disable RLS
            cursor.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):

    dependencies = [
        ('clinical', '0004_auditlog'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(enable_rls, disable_rls),
    ]

