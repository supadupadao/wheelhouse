use clap::Parser;
use lazy_static::lazy_static;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
pub struct Config {
    #[clap(
        long = "address",
        env = "SKIPPER_DAO_ADDR",
        help = "Address of deployed Skipper contract"
    )]
    pub dao_address: String,

    #[clap(long = "database", env = "SKIPPER_DB_URL", help = "Database url")]
    pub db: String,
}

pub fn conf() -> &'static Config {
    lazy_static! {
        static ref CFG: Config = Config::parse();
    }

    &CFG
}
