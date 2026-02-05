"""Create core tables

Revision ID: 9f1a2c3d4e5f
Revises: 471775a0812b
Create Date: 2026-02-03 22:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '9f1a2c3d4e5f'
down_revision = '471775a0812b'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = inspect(bind)
    tables = set(insp.get_table_names())

    if 'user' not in tables:
        op.create_table(
            'user',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('phone', sa.String(length=20), nullable=True),
            sa.Column('email', sa.String(length=150), nullable=False, unique=True),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('role', sa.String(length=20), nullable=False, server_default='user'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if 'product' not in tables:
        op.create_table(
            'product',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('price', sa.Numeric(10, 2), nullable=False),
            sa.Column('description', sa.String(length=1000), nullable=True),
            sa.Column('stock', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.true()),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if 'product_image' not in tables:
        op.create_table(
            'product_image',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False),
            sa.Column('image_path', sa.String(length=255), nullable=False),
        )

    if 'cart' not in tables:
        op.create_table(
            'cart',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if 'cart_item' not in tables:
        op.create_table(
            'cart_item',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('cart_id', sa.Integer(), sa.ForeignKey('cart.id'), nullable=False),
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=True, server_default='1'),
            sa.UniqueConstraint('cart_id', 'product_id', name='uix_cart_product'),
            sa.CheckConstraint('quantity > 0', name='ck_cartitem_qty'),
        )

    if 'order' not in tables:
        op.create_table(
            'order',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
            sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('full_name', sa.String(length=200), nullable=False),
            sa.Column('phone', sa.String(length=20), nullable=False),
            sa.Column('address', sa.String(length=500), nullable=False),
            sa.Column('city', sa.String(length=100), nullable=False),
            sa.Column('state', sa.String(length=200), nullable=False),
            sa.Column('pincode', sa.String(length=12), nullable=False),
            sa.Column('payment_id', sa.String(length=100), nullable=True),
            sa.Column('payment_status', sa.String(length=20), nullable=True, server_default='pending'),
            sa.Column('payment_method', sa.String(length=50), nullable=True),
            sa.Column('paid_at', sa.DateTime(), nullable=True),
            sa.Column('razorpay_order_id', sa.String(length=200), nullable=True),
            sa.Column('razorpay_payment_id', sa.String(length=200), nullable=True),
            sa.Column('razorpay_signature', sa.String(length=200), nullable=True),
        )
    else:
        existing_cols = {c['name'] for c in insp.get_columns('order')}
        if 'razorpay_order_id' not in existing_cols:
            op.add_column('order', sa.Column('razorpay_order_id', sa.String(length=200)))
        if 'razorpay_payment_id' not in existing_cols:
            op.add_column('order', sa.Column('razorpay_payment_id', sa.String(length=200)))
        if 'razorpay_signature' not in existing_cols:
            op.add_column('order', sa.Column('razorpay_signature', sa.String(length=200)))

    if 'order_item' not in tables:
        op.create_table(
            'order_item',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('order_id', sa.Integer(), sa.ForeignKey('order.id'), nullable=False),
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('product.id'), nullable=False),
            sa.Column('price', sa.Numeric(10, 2), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False),
        )


def downgrade():
    op.drop_table('order_item')
    op.drop_table('order')
    op.drop_table('cart_item')
    op.drop_table('cart')
    op.drop_table('product_image')
    op.drop_table('product')
    op.drop_table('user')
