use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
pub enum RPLXXVersion {
    v130,
    v140rc1,
    v140rc2,
    v140rc3,
    v140rc4,
    v140,
    v140a,
    v140b,
} // support for newer versions must manually be added!

#[derive(Serialize, Deserialize, Debug)]
pub enum SVIdentifier {
    Numeric(u64),
    AlphaNumeric(String),
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SVersion {
    pub major: u64,
    pub minor: u64,
    pub patch: u64,
    pub reltype: Vec<SVIdentifier>,
    pub build: Vec<SVIdentifier>
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Package {
    pub pkg_name: String,
    pub pkg_version: SVersion,
    pub pkg_description: String,
    pub pkg_authors: Vec<String>,
    pub pkg_license: String
}
