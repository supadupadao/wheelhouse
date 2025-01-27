use crate::consts::TON_ADDRESS_BYTES_LEN;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(DAO::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(DAO::Address)
                            .binary_len(TON_ADDRESS_BYTES_LEN)
                            .primary_key(),
                    )
                    .col(
                        ColumnDef::new(DAO::JettonAddress)
                            .binary_len(TON_ADDRESS_BYTES_LEN)
                            .unique_key()
                            .not_null(),
                    )
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(DAO::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
pub(crate) enum DAO {
    Table,
    Address,
    JettonAddress,
}
