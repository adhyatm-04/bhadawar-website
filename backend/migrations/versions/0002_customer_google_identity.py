"""Add an optional Google identity link to customer accounts."""
from alembic import op
import sqlalchemy as sa


revision = "0002_customer_google_identity"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("customer_accounts")}
    if "google_sub" not in columns:
        op.add_column("customer_accounts", sa.Column("google_sub", sa.String(), nullable=True))
        inspector = sa.inspect(bind)
    unique_constraints = inspector.get_unique_constraints("customer_accounts")
    indexes = inspector.get_indexes("customer_accounts")
    has_unique_google_sub = any(
        constraint.get("column_names") == ["google_sub"] for constraint in unique_constraints
    ) or any(
        index.get("unique") and index.get("column_names") == ["google_sub"] for index in indexes
    )
    if not has_unique_google_sub:
        op.create_unique_constraint("uq_customer_accounts_google_sub", "customer_accounts", ["google_sub"])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    unique_constraints = inspector.get_unique_constraints("customer_accounts")
    google_constraint = next((constraint.get("name") for constraint in unique_constraints
                              if constraint.get("column_names") == ["google_sub"]), None)
    if google_constraint:
        op.drop_constraint(google_constraint, "customer_accounts", type_="unique")
    columns = {column["name"] for column in inspector.get_columns("customer_accounts")}
    if "google_sub" in columns:
        op.drop_column("customer_accounts", "google_sub")
