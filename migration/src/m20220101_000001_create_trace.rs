use crate::consts::{TON_ADDRESS_BYTES_LEN, TON_TRACE_ID_LEN};
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(AccountLastTrace::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(AccountLastTrace::Account)
                            .binary_len(TON_ADDRESS_BYTES_LEN)
                            .primary_key(),
                    )
                    .col(
                        ColumnDef::new(AccountLastTrace::TraceId)
                            .string_len(TON_TRACE_ID_LEN)
                            .not_null(),
                    )
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(AccountLastTrace::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum AccountLastTrace {
    Table,
    Account,
    TraceId,
}
