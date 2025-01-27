use crate::m20250126_153838_create_dao::DAO;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(Proposal::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(Proposal::DaoAddress).binary().not_null())
                    .col(ColumnDef::new(Proposal::Id).big_integer().not_null())
                    .primary_key(Index::create().col(Proposal::DaoAddress).col(Proposal::Id))
                    .to_owned(),
            )
            .await?;
        manager
            .create_foreign_key(
                ForeignKey::create()
                    .from_tbl(Proposal::Table)
                    .from_col(Proposal::DaoAddress)
                    .to_tbl(DAO::Table)
                    .to_col(DAO::Address)
                    .name("fk_proposal_to_dao")
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Proposal::Table).to_owned())
            .await?;
        manager
            .drop_foreign_key(ForeignKey::drop().name("fk_proposal_to_dao").to_owned())
            .await?;

        Ok(())
    }
}

#[derive(DeriveIden)]
enum Proposal {
    Table,
    DaoAddress,
    Id,
}
