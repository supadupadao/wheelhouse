//! `SeaORM` Entity, @generated by sea-orm-codegen 1.1.0

use sea_orm::entity::prelude::*;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq)]
#[sea_orm(table_name = "proposal")]
pub struct Model {
    #[sea_orm(
        primary_key,
        auto_increment = false,
        column_type = "VarBinary(StringLen::None)"
    )]
    pub dao_address: Vec<u8>,
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: i64,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::dao::Entity",
        from = "Column::DaoAddress",
        to = "super::dao::Column::Address",
        on_update = "NoAction",
        on_delete = "NoAction"
    )]
    Dao,
}

impl Related<super::dao::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Dao.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
