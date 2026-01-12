"""
Database connection and utilities
MySQL connection management
"""
import pymysql
from flask import g, current_app
from contextlib import contextmanager


def get_db():
    """Get database connection from Flask g object"""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['MYSQL_HOST'],
            port=current_app.config['MYSQL_PORT'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    return g.db


def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize database (create tables if needed)"""
    with app.app_context():
        # Test connection
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")


@contextmanager
def get_cursor(commit=False):
    """Context manager for database cursor"""
    db = get_db()
    cursor = db.cursor()
    try:
        yield cursor
        if commit:
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()


def execute_query(query, params=None, commit=False, fetch_one=False, fetch_all=False):
    """
    Execute a database query
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        commit: Whether to commit the transaction
        fetch_one: Return single row
        fetch_all: Return all rows
    
    Returns:
        Query result or None
    """
    with get_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        elif commit:
            return cursor.lastrowid
        return None


def get_mysql_config():
    """Get MySQL configuration for s3.py RenderS3Client"""
    return {
        'host': current_app.config['MYSQL_HOST'],
        'port': current_app.config['MYSQL_PORT'],
        'user': current_app.config['MYSQL_USER'],
        'password': current_app.config['MYSQL_PASSWORD'],
        'database': current_app.config['MYSQL_DB']
    }






