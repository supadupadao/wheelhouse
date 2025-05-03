pub use sea_orm_migration::prelude::*;

mod consts;
mod m20250126_153838_create_dao;
mod m20250126_153851_create_proposal;

pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            Box::new(m20250126_153838_create_dao::Migration),
            Box::new(m20250126_153851_create_proposal::Migration),
        ]
    }
}
