"""Added Account class and updated User class

Revision ID: 6ab2c585fe28
Revises: 
Create Date: 2023-11-01 16:53:25.100575

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ab2c585fe28'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('food_nigerian')
    with op.batch_alter_table('grocery', schema=None) as batch_op:
        batch_op.alter_column('quantity',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('price',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               type_=sa.Float(),
               nullable=True)
        batch_op.drop_constraint('grocery_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        batch_op.alter_column('first_name',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=100),
               existing_nullable=False)
        batch_op.alter_column('last_name',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=100),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=100),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=100),
               existing_nullable=False)
        batch_op.drop_constraint('user_email_key', type_='unique')
        batch_op.create_foreign_key(None, 'account', ['account_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_unique_constraint('user_email_key', ['email'])
        batch_op.alter_column('password',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
        batch_op.alter_column('last_name',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
        batch_op.alter_column('first_name',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=255),
               existing_nullable=False)
        batch_op.drop_column('account_id')

    with op.batch_alter_table('grocery', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('grocery_user_id_fkey', 'user', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.alter_column('price',
               existing_type=sa.Float(),
               type_=sa.NUMERIC(precision=10, scale=2),
               nullable=False)
        batch_op.alter_column('quantity',
               existing_type=sa.INTEGER(),
               nullable=False)

    op.create_table('food_nigerian',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('image_source', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('name', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='food_nigerian_pkey')
    )
    op.drop_table('account')
    # ### end Alembic commands ###