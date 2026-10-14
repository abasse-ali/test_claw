'''Initial migration

Revision ID: initial
Revises: 
Create Date: 2026-10-14 00:00:00.000000
'''
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


# Price Comparator database schema

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('role', sa.Enum('user', 'admin', name='user_role'), default='user', nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('preferred_radius_km', sa.Float(), default=10.0, nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )

    # Create supermarkets table
    op.create_table('supermarkets',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, index=True),
        sa.Column('brand', sa.String(100), nullable=True),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sa.String(100), nullable=False, index=True),
        sa.Column('postal_code', sa.String(10), nullable=False),
        sa.Column('country', sa.String(2), server_default='FR', nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('opening_hours', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    )
    op.create_index('ix_supermarkets_location', 'supermarkets', ['latitude', 'longitude'], unique=False)
    op.create_index('ix_supermarkets_city_brand', 'supermarkets', ['city', 'brand'], unique=False)

    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
    )

    # Create products table
    op.create_table('products',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('slug', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('brand', sa.String(100), nullable=True, index=True),
        sa.Column('barcode', sa.String(20), nullable=True, unique=True, index=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('unit', sa.String(20), server_default='unit', nullable=False),
        sa.Column('unit_size', sa.Float(), nullable=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=True, index=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    )
    op.create_index('ix_products_brand_category', 'products', ['brand', 'category_id'], unique=False)
    op.create_index('ix_products_name_brand', 'products', ['name', 'brand'], unique=False)

    # Create prices table
    op.create_table('prices',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False, index=True),
        sa.Column('supermarket_id', sa.Integer(), sa.ForeignKey('supermarkets.id'), nullable=False, index=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('original_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_promotion', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('promotion_label', sa.String(100), nullable=True),
        sa.Column('promotion_end_date', sa.DateTime(), nullable=True),
        sa.Column('currency', sa.String(3), server_default='EUR', nullable=False),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('scraped_at', sa.DateTime(), default=datetime.utcnow, nullable=False, index=True),
        sa.Column('is_available', sa.Boolean(), default=True, nullable=False),
    )
    op.create_index('ix_prices_product_supermarket_date', 'prices', ['product_id', 'supermarket_id', 'scraped_at'], unique=False)
    op.create_index('ix_prices_product_date', 'prices', ['product_id', 'scraped_at'], unique=False)
    op.create_unique_constraint('uq_price_product_supermarket_date', 'prices', ['product_id', 'supermarket_id', 'scraped_at'])

    # Create price_history table
    op.create_table('price_history',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False, index=True),
        sa.Column('supermarket_id', sa.Integer(), sa.ForeignKey('supermarkets.id'), nullable=False, index=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('original_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_promotion', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('recorded_at', sa.DateTime(), default=datetime.utcnow, nullable=False, index=True),
    )
    op.create_index('ix_price_history_product_supermarket_date', 'price_history', ['product_id', 'supermarket_id', 'recorded_at'], unique=False)

    # Create price_alerts table
    op.create_table('price_alerts',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False, index=True),
        sa.Column('supermarket_id', sa.Integer(), sa.ForeignKey('supermarkets.id'), nullable=True, index=True),
        sa.Column('target_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('current_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('notify_email', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('notify_push', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    )

    # Create user_favorites table
    op.create_table('user_favorites',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
    )
    op.create_unique_constraint('uq_user_favorite_product', 'user_favorites', ['user_id', 'product_id'])

    # Create user_favorite_supermarkets table
    op.create_table('user_favorite_supermarkets',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('supermarket_id', sa.Integer(), sa.ForeignKey('supermarkets.id'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
    )
    op.create_unique_constraint('uq_user_favorite_supermarket', 'user_favorite_supermarkets', ['user_id', 'supermarket_id'])

    # Create scraping_jobs table
    op.create_table('scraping_jobs',
        sa.Column('id', sa.Integer(), sa.Identity(), primary_key=True),
        sa.Column('supermarket_id', sa.Integer(), sa.ForeignKey('supermarkets.id'), nullable=False, index=True),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('products_scraped', sa.Integer(), server_default='0', nullable=False),
        sa.Column('products_updated', sa.Integer(), server_default='0', nullable=False),
        sa.Column('products_new', sa.Integer(), server_default='0', nullable=False),
        sa.Column('errors', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
    )


def downgrade():
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('scraping_jobs')
    op.drop_table('user_favorite_supermarkets')
    op.drop_table('user_favorites')
    op.drop_table('price_alerts')
    op.drop_table('price_history')
    op.drop_constraint('uq_price_product_supermarket_date', 'prices', type_='unique')
    op.drop_index('ix_prices_product_date', table_name='prices')
    op.drop_index('ix_prices_product_supermarket_date', table_name='prices')
    op.drop_table('prices')
    op.drop_index('ix_products_name_brand', table_name='products')
    op.drop_index('ix_products_brand_category', table_name='products')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_index('ix_supermarkets_city_brand', table_name='supermarkets')
    op.drop_index('ix_supermarkets_location', table_name='supermarkets')
    op.drop_table('supermarkets')
    op.drop_table('users')